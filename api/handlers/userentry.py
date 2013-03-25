'''
Created on Oct 19, 2012

@author: howard
'''

import logging
import json
import urllib
import calendar
from datetime import datetime

from piston.handler import BaseHandler
from piston.utils import rc

from rdflib import URIRef, Graph, Namespace, Literal, plugin
from rdflib.store import Store, VALID_STORE
from rdflib import RDF, RDFS

from api.models import Entry

from api import _get_db_config_string, SCHEMA_GRAPH_URI, USER_GRAPH_URI, DATABASE_STORE

from . import get_predicate_lookup_for

logger = logging.getLogger(__name__)

def _get_entry_json_obj(g, entryURIRef):

  entryURIStr = str(entryURIRef)

  # select all the predicates and objects for this subject
  query = ' \
    SELECT ?predicate ?object \
    WHERE {{ \
      <{0}> ?predicate ?object \
    }}'.format(str(entryURIStr))
  
  rs = g.query(query)

  values = [{'predicate': t[0], 'object': t[1]} for t in rs]

  return {'uri': urllib.quote(entryURIStr), 'values': values, 'schema': None}
    
class UserEntryHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  fields = ('name', 'email')

  def _get_image_json_obj(self, entry):
    images_obj = []
    images = entry.entryimage_set.all()
    if images:
      for image in images:
        images_obj.append(image.to_json_obj());
    return images_obj

  def read(self, request, user_id, entry_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')

    rt = store.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE,"The underlying store is corrupted"

    try:
      
      ug = Graph(store, identifier=URIRef(str(USER_GRAPH_URI).format(userId=user_id)))
  
      result = None
      
      if entry_id:

        entryURI = URIRef(urllib.unquote(entry_id))
        result = _get_entry_json_obj(ug, entryURI)

      else:

        # will need to schema graph for this
        sg = Graph(store, identifier=URIRef(SCHEMA_GRAPH_URI))

        schemaNS = Namespace(SCHEMA_GRAPH_URI)

        # check for filter criteria; if none exists default to all items
        parentClass = None
        if 'filter' in request.GET:
          parentClass = schemaNS[request.GET['filter']]
        else:
          parentClass = schemaNS['Collectable']

        # get the list of candidate classes from the schema graph and then query the user's
        # graph for all instances of those classes and order them by creation time
        candidateClasses = sg.transitive_subjects(RDFS['subClassOf'], parentClass)
        
        filterStr = None
        for cc in candidateClasses:
          filterStr = '{0} || STRSTARTS(STR(?class), "{1}")'.format(filterStr, cc) if filterStr else 'STRSTARTS(STR(?class), "{0}")'.format(cc)
        
        query = ' \
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
          PREFIX dc: <http://purl.org/dc/elements/1.1/> \
          PREFIX sg: <{0}> \
          SELECT ?subject ?class ?createTime ?title ?description ?acquirePrice \
          WHERE {{ \
            ?subject rdf:type ?class ; \
                     sg:createTime ?createTime \
            OPTIONAL {{ ?subject dc:title ?title }} \
            OPTIONAL {{ ?subject dc:description ?description }} \
            OPTIONAL {{ ?subject sg:acquirePrice ?acquirePrice }} \
            FILTER ({1}) \
          }} \
          ORDER BY DESC(?createTime)'
        
        query = query.format(SCHEMA_GRAPH_URI, filterStr)

        rs = ug.query(query)
        
        result = [{'id': urllib.quote(t[0]),
                   'create_time': t[2],
                   'title': t[3],
                   'description': t[4],
                   'acquire_price': t[5],
                   'type': urllib.quote(t[1])} for t in rs]

    finally:
      store.close()

    return result

  def create(self, request, user_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only create your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    rdfType = RDF['type']
    rdfTypeStr = str(rdfType)
  
    try:
      body_obj = json.loads(request.body)
      
      # check for existance and determine class
      classURIRef = None
      for valuePair in body_obj.get('values',[]):
        if valuePair.get('predicate') == rdfTypeStr:
          classURIRef = URIRef(urllib.unquote(valuePair.get('object')))
          break
      
      if not classURIRef:
        resp = rc.BAD_REQUEST
        resp.write (' - missing required entry predicate: ' + rdfTypeStr)
        return resp

    except:
      return rc.BAD_REQUEST

    try:
      entry = Entry(user_id=user_id)
      entry.save()
    except Exception, e:
      resp = rc.INTERNAL_ERROR
      resp.write(' - ' + str(e))
      return resp

    # connect to the graph db
    store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')
    rt = store.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE,"The underlying store is corrupted"

    try:
      schemaNS = Namespace(SCHEMA_GRAPH_URI)
      userNS = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      g = Graph(store, identifier=URIRef(userNS))
      sg = Graph(store, identifier=URIRef(schemaNS))

      # get the schema for the specified type
      lookup = get_predicate_lookup_for(sg, classURIRef)

      entryURIRef = userNS[str(entry.id)]

      # handle createTime, updateTime, and type specially
      g.add((entryURIRef, rdfType, classURIRef))

      now = datetime.now()
      timestamp = calendar.timegm(now.timetuple())
      
      g.add((entryURIRef, schemaNS['createTime'], Literal(timestamp)))
      g.add((entryURIRef, schemaNS['updateTime'], Literal(timestamp)))
      
      for valuePair in body_obj.get('values',[]):
        
        print valuePair.get('predicate'), ' -> ', valuePair.get('object')

        # type is handled specially
        if valuePair.get('predicate') == rdfTypeStr:
          continue

        predicateSchema = lookup.get(valuePair.get('predicate'))
        if not predicateSchema:
          print "Cannot find schema for {0}- skipping property".format(valuePair.get('predicate'))
          continue
        
        objectRef = None
        
        typeUri = str(predicateSchema['type']) 
        if typeUri == 'http://www.w3.org/2002/07/owl#DatatypeProperty' or typeUri == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property':
          objectRef = Literal(valuePair.get('object'))
        elif typeUri == 'http://www.w3.org/2002/07/owl#ObjectProperty':
          objectRef = URIRef(valuePair.get('object'))
        else:
          raise Exception("Only support owl:DatatypeProperty, rdf:Property and owl:ObjectProperty properties")
                                                            
        g.add((entryURIRef, URIRef(valuePair.get('predicate')), objectRef))

      g.commit()

      result = _get_entry_json_obj(g, entryURIRef)

    finally:
      store.close()

    return result
  
  def update(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only update your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:
      #body_obj = json.loads(request.body)
      pass

    except:
      return rc.BAD_REQUEST

    return {}

  def delete(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    # can only delete your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    return {}

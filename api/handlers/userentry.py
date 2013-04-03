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
from rdflib import RDF, RDFS, OWL

from api.models import Entry

from api import _get_db_config_string, SCHEMA_GRAPH_URI, USER_GRAPH_URI, DATABASE_STORE

from . import get_schema_and_lookup_for, get_full_schema_for, SCHEMA

import rdfutils

logger = logging.getLogger(__name__)

def _get_entry_json_obj(ug, sg, entryURIRef):

  entryURIStr = str(entryURIRef)

  # select all the predicates and objects for this subject
  query = ' \
    SELECT ?predicate ?object \
    WHERE {{ \
      <{0}> ?predicate ?object \
    }}'.format(str(entryURIStr))
  
  rs = ug.query(query)

  data = {}
  for t in rs:
    data[str(t[0])] = str(t[1])

  # find the type of the object so we can query for its schema
  typePred = RDF['type']
  typeVal = data.get(str(typePred))

  if not typeVal:
    raise Exception('Invalid state: entry missing required RDF[\'type\']')

  return {'id': urllib.quote(entryURIStr), 'data': data, 'schema': get_full_schema_for(typeVal, sg)}
    
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
      sg = Graph(store, identifier=URIRef(SCHEMA_GRAPH_URI))

      DC = Namespace('http://purl.org/dc/elements/1.1/')

      result = None
      
      if entry_id:

        entryURI = URIRef(urllib.unquote(entry_id))
        result = _get_entry_json_obj(ug, sg, entryURI)

      else:

        # check for filter criteria; if none exists default to all items
        parentClass = None
        if 'filter' in request.GET:
          parentClass = SCHEMA[request.GET['filter']]
        else:
          parentClass = SCHEMA['Collectable']

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
          SELECT ?subject ?class ?createTime ?title ?description ?acquirePrice ?media \
          WHERE {{ \
            ?subject rdf:type ?class ; \
                     sg:createTime ?createTime \
            OPTIONAL {{ ?subject sg:media ?media }} \
            OPTIONAL {{ ?subject dc:title ?title }} \
            OPTIONAL {{ ?subject dc:description ?description }} \
            OPTIONAL {{ ?subject sg:acquirePrice ?acquirePrice }} \
            FILTER ({1}) \
          }} \
          ORDER BY DESC(?createTime)'
        
        query = query.format(SCHEMA_GRAPH_URI, filterStr)

        rs = ug.query(query)
        
        result = [{'id': urllib.quote(t[0]),
                   'data': {
                     str(RDF['type']): t[1], 
                     str(SCHEMA['createTime']): t[2],
                     str(DC['title']): t[3],
                     str(DC['description']): t[4],
                     str(SCHEMA['acquirePrice']): t[5]
                   },
                   'schema': None } for t in rs]
                   

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
      
    except:
      return rc.BAD_REQUEST

    # check for existance and determine class
    data = body_obj.get('data',[])
    classURI = data.get(rdfTypeStr)
    if not classURI:
      resp = rc.BAD_REQUEST
      resp.write (' - missing required predicate: ' + rdfTypeStr)
      return resp

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

      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      ug = Graph(store, identifier=URIRef(USER))
      sg = Graph(store, identifier=URIRef(SCHEMA))

      # inject id into JSON
      body_obj['id'] = USER[str(entry.id)]

      entryURIRef = rdfutils.object_from_json(sg, ug, body_obj, None, None)
      
      now = datetime.now()
      timestamp = calendar.timegm(now.timetuple())
       
      ug.add((entryURIRef, SCHEMA['createTime'], Literal(timestamp)))
      ug.add((entryURIRef, SCHEMA['updateTime'], Literal(timestamp)))
      
      ug.commit()

      result = _get_entry_json_obj(ug, sg, entryURIRef)

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

    # connect to the graph db
    store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')
    rt = store.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE,"The underlying store is corrupted"

    try:
      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      ug = Graph(store, identifier=URIRef(USER))

      entryURIRef = URIRef(urllib.unquote(entry_id))

      result = _get_entry_json_obj(ug, entryURIRef)

    finally:
      store.close()

    return result

  def delete(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    # can only delete your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    return {}

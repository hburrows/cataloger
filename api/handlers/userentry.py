'''
Created on Oct 19, 2012

@author: howard
'''

import logging
import json
import urllib

from piston.handler import BaseHandler
from piston.utils import rc

from rdflib import ConjunctiveGraph, URIRef, Graph, Namespace, Literal
from rdflib.store import VALID_STORE
from rdflib import RDF

from api.models import Entry

from . import _get_db_config_string, BASE_GRAPH_URI, SCHEMA_GRAPH_URI, USER_GRAPH_URI, get_predicate_lookup_for

logger = logging.getLogger(__name__)

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

    if entry_id:
      return {}
    else:
      return []

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
    citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(BASE_GRAPH_URI))
    rt = citg.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE, "The underlying store is corrupted"

    try:
      userNS = Namespace(str(USER_GRAPH_URI).format(userId=user_id))
      g = Graph(citg.store, identifier=URIRef(userNS))
      sg = Graph(citg.store, identifier=URIRef(SCHEMA_GRAPH_URI))
      

      # get the schema for the specified type
      lookup = get_predicate_lookup_for(sg, classURIRef)

      entryUri = userNS[str(entry.id)]

      for valuePair in body_obj.get('values',[]):
        
        print valuePair.get('predicate'), ' -> ', valuePair.get('object')

        # type is handled specially
        if valuePair.get('predicate') == rdfTypeStr:
          g.add((entryUri, rdfType, classURIRef))
        else:
          predicateSchema = lookup.get(valuePair.get('predicate'))
          if not predicateSchema:
            print "Cannot find schema for {0}- skipping property".format(valuePair.get('predicate'))
            continue
          
          objectRef = None
          
          typeUri = str(predicateSchema['type']) 
          if typeUri == 'http://www.w3.org/2002/07/owl#DatatypeProperty':
            objectRef = Literal(valuePair.get('object'))
          elif predicateSchema['type'] == 'http://www.w3.org/2002/07/owl#ObjectProperty':
            objectRef = URIRef(valuePair.get('object'))
          else:
            raise Exception("Only support DatatypeProperty and ObjectProperty properties")
                                                              
          g.add((entryUri, URIRef(valuePair.get('predicate')), objectRef))
        
      citg.commit()
      citg.close()

    except Exception, e:
      citg.close()
      raise e;

    return {}
  
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

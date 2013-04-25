'''
Created on Oct 19, 2012

@author: howard
'''

import logging
import json

from piston.handler import BaseHandler
from piston.utils import rc

from rdflib import URIRef, Namespace
from rdflib import RDF

from . import sparql_query

from api.models import Entry

from api import COMMON_GRAPH_URI, USER_GRAPH_URI

from . import SCHEMA

import rdfutils

logger = logging.getLogger(__name__)

  
class UserEntryHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  fields = ('name', 'email')

  def read(self, request, user_id, entry_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:

      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      DC = Namespace('http://purl.org/dc/elements/1.1/')

      result = None
      
      if entry_id:

        result = rdfutils.object_to_json(COMMON_GRAPH_URI, USER, entry_id)

      else:

        # check for filter criteria; if none exists default to all items
        root_type_uri = None
        if 'filter' in request.GET:
          root_type_uri = SCHEMA[request.GET['filter']]
        else:
          root_type_uri = SCHEMA['Collectable']

          rq_tmpl = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX cg: <{cg}>
PREFIX : <{ug}>
SELECT ?s ?class ?createTime ?title ?description ?acquirePrice ?thumbnailURL ?classLabel
#FROM NAMED <{ug}>
#FROM NAMED <{cg}>
WHERE {{
  {{
    GRAPH cg: {{
      <{type}> rdfs:label ?classLabel .
      BIND (<{type}> AS ?class)
    }}
  }}
  UNION
  {{
    GRAPH cg: {{
      ?class rdfs:subClassOf+ <{type}> .
      ?class rdfs:label ?classLabel .
    }}
  }}
  GRAPH : {{
    ?s rdf:type ?class .
    ?s cg:createTime ?createTime .
    OPTIONAL {{ ?s dc:title ?title }}             
    OPTIONAL {{ ?s dc:description ?description }}             
    OPTIONAL {{ ?s cg:acquirePrice ?acquirePrice }}
    OPTIONAL {{
      # get the thumbnail image for the first StillImage media object
      ?s cg:media ?media .
      ?media ?seq_index ?media_item .
      ?media_item rdf:type cg:StillImage .
      ?media_item cg:images ?media_item_seq .
      ?media_item_seq ?media_item_seq_index ?media_item_instance .
      ?media_item_instance cg:stillImageType "thumbnail" .
      ?media_item_instance cg:stillImageURL ?thumbnailURL .
    }}      
  }}
}}
ORDER BY DESC(?createTime)
'''

        rq = rq_tmpl.format(type=root_type_uri, ug=USER, cg=COMMON_GRAPH_URI)

        result = [{'id': t['s']['value'],
                   'data': {
                     str(RDF['type']): t['class']['value'],
                     str(SCHEMA['type-label']): t['classLabel']['value'], 
                     str(SCHEMA['createTime']): t['createTime']['value'],
                     str(DC['title']): t['title']['value'] if 'title' in t else None,
                     str(DC['description']): t['description']['value'] if 'description' in t else None,
                     str(SCHEMA['acquirePrice']): t['acquirePrice']['value'] if 'acquirePrice' in t else None,
                     str(SCHEMA['stillImageURL']): t['thumbnailURL']['value'] if 'thumbnailURL' in t else None
                   },
                   'schema': None } for t in sparql_query(rq)["results"]["bindings"]]
        
    except Exception, e:
      raise e

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

    try:

      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      # inject id into JSON
      entry_uri = USER[str(entry.id)]
      body_obj['id'] = entry_uri 

      rdfutils.update_from_json(USER, COMMON_GRAPH_URI, entry_uri, body_obj)

      result = rdfutils.object_to_json(COMMON_GRAPH_URI, USER, entry_uri)

    except:
      raise

    return result
  
  def update(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only update your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:
      body_obj = json.loads(request.body)
      
      if not body_obj.get('id'):
        resp = rc.BAD_REQUEST
        resp.write('.  Missing required \'id\' property')
        return resp

    except:
      resp = rc.BAD_REQUEST
      resp.write('.  Error parsing JSON')
      return resp

    try:
      
      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      # inject id into JSON
      entry_uri = body_obj['id']

      rdfutils.update_from_json(USER, COMMON_GRAPH_URI, entry_uri, body_obj)

      result = rdfutils.object_to_json(COMMON_GRAPH_URI, USER, entry_uri)

    except Exception, e:
      raise e

    return result

  def delete(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    # can only delete your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    return {}

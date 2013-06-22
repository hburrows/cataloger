'''
Created on Oct 19, 2012

@author: howard
'''

import logging
import json
import calendar
import uuid

import dateutil.parser

from piston.handler import BaseHandler
from piston.utils import rc

from rdflib import Namespace, RDF

from api import COMMON_GRAPH_URI, USER_GRAPH_URI

from . import sparql_query, SCHEMA, sparql_froms_for_user


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

        result = rdfutils.object_to_json(sparql_froms_for_user(request.user), COMMON_GRAPH_URI, USER, entry_id)

      else:

        # check for filter criteria; if none exists default to all items
        root_type_uri = None
        if 'filter' in request.GET:
          root_type_uri = SCHEMA[request.GET['filter']]
        else:
          root_type_uri = SCHEMA['Entry']

          rq_tmpl = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX common: <{cg}>
PREFIX : <{ug}>
SELECT ?s ?class ?createTime ?title ?description ?acquirePrice ?thumbnailURL ?classLabel
{graphs}
FROM NAMED :
WHERE {{
  {{
    <{type}> rdfs:label ?classLabel .
    BIND (<{type}> AS ?class)
  }}
  UNION
  {{
    ?class rdfs:subClassOf+ <{type}> .
    ?class rdfs:label ?classLabel .
  }}
  GRAPH : {{
    ?s rdf:type ?class .
    ?s common:createTime ?createTime .
    OPTIONAL {{ ?s dc:title ?title }}             
    OPTIONAL {{ ?s dc:description ?description }}             
    OPTIONAL {{ ?s common:acquirePrice ?acquirePrice }}
    OPTIONAL {{
      # get the thumbnail image for the first StillImage media object
      ?s common:media ?media .
      ?media ?seq_index ?media_item .
      ?media_item rdf:type common:StillImage .
      ?media_item common:images ?media_item_seq .
      ?media_item_seq ?media_item_seq_index ?media_item_instance .
      ?media_item_instance common:stillImageType "thumbnail" .
      ?media_item_instance common:stillImageURL ?thumbnailURL .
    }}      
  }}
}}
ORDER BY DESC(?createTime)
'''

        rq = rq_tmpl.format(graphs=sparql_froms_for_user(request.user), type=root_type_uri, ug=USER, cg=COMMON_GRAPH_URI)

        result = [{'id': t['s']['value'],
                   'graph': USER,
                   'data': {
                     str(RDF['type']): t['class']['value'],
                     str(SCHEMA['type-label']): t['classLabel']['value'], 
                     str(SCHEMA['createTime']): calendar.timegm(dateutil.parser.parse(t['createTime']['value']).timetuple()),
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

    USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

    subjectId = uuid.uuid4().hex
    
    # inject the new subject-id into the JSON
    subject_uri = USER[subjectId]
    body_obj['id'] = subject_uri 

    try:

      rdfutils.update_from_json(sparql_froms_for_user(request.user), USER, COMMON_GRAPH_URI, subject_uri, body_obj)

      result = rdfutils.object_to_json(sparql_froms_for_user(request.user), COMMON_GRAPH_URI, USER, subject_uri)

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
      
    except:
      resp = rc.BAD_REQUEST
      resp.write('.  Error parsing JSON')
      return resp

    if not body_obj.get('id'):
      resp = rc.BAD_REQUEST
      resp.write('.  Missing required \'id\' property')
      return resp

    if body_obj['id'] != entry_id:
      resp = rc.BAD_REQUEST
      resp.write('.  Arguments don\'t match payload')
      return resp

    try:
      
      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      # inject id into JSON
      entry_uri = body_obj['id']

      rdfutils.update_from_json(sparql_froms_for_user(request.user), USER, COMMON_GRAPH_URI, entry_uri, body_obj)

      result = rdfutils.object_to_json(sparql_froms_for_user(request.user), COMMON_GRAPH_URI, USER, entry_uri)

    except Exception, e:
      raise e

    return result

  def delete(self, request, user_id, entry_id=None):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))
      
    if entry_id:
      # can only delete your own entries
      if not request.user.is_superuser and int(user_id) != request.user.id:
        return rc.FORBIDDEN
  
      rdfutils.delete(sparql_froms_for_user(request.user), USER, COMMON_GRAPH_URI, entry_id)
    else:
      rdfutils.delete_graph(USER)

    return rc.DELETED

'''
Created on Apr 26, 2013

@author: howard
'''

import calendar

import dateutil.parser
from piston.handler import BaseHandler
from piston.utils import rc

from rdflib import Namespace, RDF
from api import COMMON_GRAPH_URI, USER_GRAPH_URI

from . import sparql_query, SCHEMA, sparql_froms_for_user

import rdfutils

DC = Namespace('http://purl.org/dc/elements/1.1/')


class SubjectEntryHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  fields = ('name', 'email')

  def read(self, request, user_id, subject_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:

      USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

      result = None
      
      if subject_id:

        result = rdfutils.object_to_json(sparql_froms_for_user(request.user), COMMON_GRAPH_URI, USER, subject_id)

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
PREFIX common: <{cg}>
PREFIX : <{ug}>
SELECT ?s ?class ?classLabel
WHERE {{
  GRAPH : {{
    ?s rdf:type ?class .
  }}
  GRAPH common: {{
    ?class rdfs:label ?classLabel
  }}
  FILTER (!isBlank(?s))
}}
'''

        rq = rq_tmpl.format(type=root_type_uri, ug=USER, cg=COMMON_GRAPH_URI)

        result = [{'id': t['s']['value'],
                   'data': {
                     str(RDF['type']): t['class']['value'],
                     str(SCHEMA['type-label']): t['classLabel']['value'], 
                   },
                   'schema': None } for t in sparql_query(rq)["results"]["bindings"]]

    except Exception, e:
      raise e

    return result

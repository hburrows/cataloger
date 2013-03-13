'''
Created on Mar 8, 2013

@author: howard
'''


from piston.handler import BaseHandler

from rdflib import ConjunctiveGraph, Graph, URIRef
from rdflib.store import VALID_STORE

import urllib
from base64 import urlsafe_b64encode
from . import BASE_GRAPH_URI, SCHEMA_GRAPH_URI, _get_postgresql_config_string


#from api.models import User

class ClassesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id=None):

    citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(BASE_GRAPH_URI))
    
    rt = citg.open(_get_postgresql_config_string(), create=False)
    
    assert rt == VALID_STORE,"The underlying store is corrupted"

    g = Graph(citg.store, SCHEMA_GRAPH_URI)
    
    # what is the prefix for this graph

    rs = g.query(
      'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
       PREFIX owl: <http://www.w3.org/2002/07/owl#> \
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
       PREFIX sg: <http://example.com/rdf/schemas/> \
       SELECT ?class \
       WHERE { { ?class rdf:type owl:Class . ?class sg:isUsedBy "catalogit" OPTIONAL { ?class rdfs:label ?label } } \
       UNION { ?class rdf:type rdfs:Class . ?class sg:isUsedBy "catalogit" OPTIONAL { ?class rdfs:label ?label } } } \
       ORDER BY ?label')

    classes = []
    for cls in rs:

      l = g.preferredLabel(cls[0])

      classes.append({
        'name': l[0][1] if len(l) > 0 else '',
        'class': urllib.quote(cls[0]),
        'comment': g.comment(cls[0]),
      })
        
    citg.close()

    return classes

  def create(self, request):
    pass


  
  
  
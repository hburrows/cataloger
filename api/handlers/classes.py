'''
Created on Mar 8, 2013

@author: howard
'''


from piston.handler import BaseHandler

from rdflib import Graph, plugin
from rdflib.store import Store,VALID_STORE

import urllib
from api import SCHEMA_GRAPH_URI, _get_db_config_string, DATABASE_STORE


#from api.models import User

class ClassesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id=None):

    store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')
    
    rt = store.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE,"The underlying store is corrupted"
       
    try:

      g = Graph(store, SCHEMA_GRAPH_URI)
      
      # what is the prefix for this graph
  
      rs = g.query(
        'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
         PREFIX owl: <http://www.w3.org/2002/07/owl#> \
         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
         PREFIX sg: <http://example.com/rdf/schemas/> \
         SELECT ?class \
         WHERE { { ?class rdf:type owl:Class . ?class sg:isUsedFor "primary" OPTIONAL { ?class rdfs:label ?label } } \
         UNION { ?class rdf:type rdfs:Class . ?class sg:isUsedFor "primary" OPTIONAL { ?class rdfs:label ?label } } } \
         ORDER BY ?label')
  
      classes = []
      for cls in rs:
  
        l = g.preferredLabel(cls[0])
  
        classes.append({
          'id': urllib.quote(cls[0]),
          'name': l[0][1] if len(l) > 0 else '',
          'class': urllib.quote(cls[0]),  # deprecated
          'comment': g.comment(cls[0]),
        })

    finally:
      store.close()

    return classes

  def create(self, request):
    pass


  
  
  
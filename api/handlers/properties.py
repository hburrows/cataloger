'''
Created on Mar 8, 2013

@author: howard
'''

from piston.handler import BaseHandler

from rdflib import URIRef, Graph, plugin
from rdflib.store import Store, VALID_STORE

from api import DATABASE_STORE, SCHEMA_GRAPH_URI, _get_db_config_string

from . import get_full_schema_for

class PropertiesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id):

    store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')
    
    rt = store.open(_get_db_config_string(), create=False)
    assert rt == VALID_STORE,"The underlying store is corrupted"
       
    try:

      g = Graph(store, SCHEMA_GRAPH_URI)

      classURI = URIRef(class_id)

      result = get_full_schema_for(classURI, g)

    finally:
      store.close()

    return result
  

  def create(self, request):
    pass


  
  
  
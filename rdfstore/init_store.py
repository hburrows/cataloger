'''
Created on Mar 7, 2013

@author: howard
'''

from rdflib import ConjunctiveGraph
from rdflib import plugin
from rdflib.store import Store
from rdflib.store import VALID_STORE
from rdflib import URIRef

from api import BASE_GRAPH_URI, DATABASE_STORE, _get_db_config_string

store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')

rt = store.open(_get_db_config_string(), create=True)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef(BASE_GRAPH_URI))

citg.commit()

citg.close()


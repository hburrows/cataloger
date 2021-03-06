'''
Created on Mar 7, 2013

@author: howard
'''

from rdflib import ConjunctiveGraph, plugin
from rdflib.store import Store, VALID_STORE
from rdflib import URIRef

from api import BASE_GRAPH_URI, _get_mysql_config_string


store = plugin.get('MySQL', Store)(identifier='rdfstore')

rt = store.open(_get_mysql_config_string(), create=True)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef(BASE_GRAPH_URI))

'''
citg = ConjunctiveGraph('MySQL', identifier=URIRef(BASE_GRAPH_URI))

rt = citg.open(_get_mysql_config_string(), create=True)

assert rt == VALID_STORE,"The underlying store is corrupted"
'''

citg.commit()

citg.close()

store.close()

print "Successfully initialized database"
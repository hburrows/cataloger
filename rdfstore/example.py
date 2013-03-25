'''
Created on Mar 21, 2013

@author: howard
'''

from rdflib import URIRef, Graph, ConjunctiveGraph, plugin
from rdflib.store import Store, VALID_STORE
from rdflib import RDF, OWL

store = plugin.get('MySQL', Store)(identifier='rdfstore')

configStr = 'host={0},user={1},password={2},db={3}'.format('localhost', '<<username>>', '<<password>>', 'rdfstore')
rt = store.open(configStr, create=True)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef('http://example.com/rdf/'))

sg = Graph(store, identifier=URIRef('http://example.com/rdf/schemas/'))

# owl
sg.parse('http://www.w3.org/2002/07/owl')

# RDFS and RDF vocabularies
sg.parse('http://www.w3.org/2000/01/rdf-schema#')
sg.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# DC vocabularies
sg.parse('http://purl.org/dc/elements/1.1/')
sg.parse('http://purl.org/dc/terms/')

# FOAF
sg.parse('http://xmlns.com/foaf/0.1/')

# Add a simple triple
sg.add((URIRef('http://example.com/rdf/schemas/MyClass'), RDF['type'], OWL['Class']))

sg.commit()

store.close()

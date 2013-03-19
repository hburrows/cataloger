'''
Created on Mar 8, 2013

@author: howard
'''

import rdflib
from rdflib import ConjunctiveGraph, Graph
from rdflib import plugin
from rdflib.store import Store
from rdflib.store import VALID_STORE
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from pprint import pprint

from rdflib import RDF, RDFS, OWL, XSD

from globals import DEFAULT_GRAPH_URI, SCHEMA_GRAPH_URI, DB, _get_postgresql_config_string

citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(DEFAULT_GRAPH_URI))

rt = citg.open(_get_postgresql_config_string(), create=False)

assert rt == VALID_STORE,"The underlying store is corrupted"

print("Triples in graph: {0}".format(len(citg)))

initNs = {
  'cit': Namespace(SCHEMA_GRAPH_URI),
  'rdf': RDF,
  'owl': OWL,
  'rdfs': RDFS
}

# CONTEXTS

for c in citg.contexts():
  print c


sg = Graph(citg.store, identifier=URIRef(SCHEMA_GRAPH_URI))

g = sg

# SUBJECTS
for s in g.query('SELECT ?subject WHERE { ?subject ?predicate ?object }', initNs=initNs):
  print s


# CLASSES
for s in g.subjects(URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),URIRef('http://www.w3.org/2002/07/owl#Class')):
  print s

# look for both owl and rdfs Classes
for s in g.query('SELECT ?subject WHERE { { ?subject rdf:type owl:Class } UNION { ?subject rdf:type rdfs:Class } }', initNs=initNs):
  print s 


# PROPERTIES OF Collectable
for t in g.triples((URIRef('http://example.com/rdf/_shared/Collectable'),None,None)):
  print t


rs = g.query('SELECT ?property ?label WHERE { ?property rdfs:domain <http://example.com/rdf/_shared/Collectable> . \
            ?property rdfs:label ?label }', initNs=initNs)

rs = g.query(
"""
SELECT ?label
WHERE { <http://purl.org/dc/elements/1.1/title> <http://www.w3.org/2000/01/rdf-schema#label> ?label }
"""
)

for r in rs:
  print r


rs = g.query(
"""
PREFIX cit: <http://example.com/rdf/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?node ?attr ?val
WHERE { ?node ?attr ?val }
ORDER BY ?node
"""
)

for r in rs:
  print r

'''
Created on Mar 11, 2013

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

from globals import DEFAULT_GRAPH_URI, SCHEMA_GRAPH_URI, _get_postgresql_config_string

citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(DEFAULT_GRAPH_URI))
rt = citg.open(_get_postgresql_config_string(), create=False)

assert rt == VALID_STORE,"The underlying store is corrupted"

sg = Graph(citg.store, identifier=URIRef(SCHEMA_GRAPH_URI))
g = sg


# query for all classes
#
rs = g.query(
  'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
   PREFIX owl: <http://www.w3.org/2002/07/owl#> \
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
   PREFIX sg: <http://example.com/rdf/schemas/> \
   SELECT ?class \
   WHERE { { ?class rdf:type owl:Class . ?class sg:isUsedFor "primary" OPTIONAL { ?class rdfs:label ?label } } \
   UNION { ?class rdf:type rdfs:Class . ?class sg:isUsedFor "primary" OPTIONAL { ?class rdfs:label ?label } } } \
   ORDER BY ?label')
    
    
# query schema related to class
#
classUri = 'http://example.com/rdf/schemas/Collectable'
classUriRef = URIRef(classUri)

rs = g.query(' \
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
  PREFIX owl: <http://www.w3.org/2002/07/owl#> \
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
  SELECT ?property ?label ?type ?range \
  WHERE { \
    { ?property rdfs:domain <' + str(classUriRef) + '> . \
      ?property rdfs:label ?label \
      OPTIONAL { ?property rdfs:range ?range } \
      OPTIONAL { ?property rdf:type ?type } \
      FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#ObjectProperty")) \
    } \
    UNION \
    { ?property rdfs:domain <' + str(classUriRef) + '> . \
      ?property rdfs:label ?label \
      OPTIONAL { ?property rdfs:range ?range } \
      OPTIONAL { ?property rdf:type ?type } \
      FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#DatatypeProperty")) \
    } \
  } \
  ORDER BY ?label')


uriRef = classUriRef 
rs = g.query(' \
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
  PREFIX owl: <http://www.w3.org/2002/07/owl#> \
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
  SELECT ?property ?label ?range ?type \
  WHERE { { ?property rdfs:domain <' + str(uriRef) + '> \
            OPTIONAL { ?property rdfs:label ?label } \
            OPTIONAL { ?property rdfs:range ?range } \
            OPTIONAL { ?property rdf:type ?type } } \
  UNION { ?property rdfs:domain <' + str(uriRef) + '> \
            OPTIONAL { ?property rdfs:label ?label } \
            OPTIONAL { ?property rdfs:range ?range } \
            OPTIONAL { ?property rdf:type ?type } } } \
  ORDER BY ?label')

# query for all contexts and all properties related by domain
#
for ctx in citg.contexts():
  g = Graph(citg.store, ctx.identifier)
  rs = g.query(' \
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
    PREFIX owl: <http://www.w3.org/2002/07/owl#> \
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
    SELECT ?class ?label \
    WHERE { { ?class rdf:type owl:Class OPTIONAL { ?class rdfs:label ?label } } \
    UNION { ?class rdf:type rdfs:Class OPTIONAL { ?class rdfs:label ?label } } } \
    ORDER BY ?label')
  for c in rs:
    print c[0], ' -----'
    print
    rs2 = g.query(' \
      PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
      PREFIX owl: <http://www.w3.org/2002/07/owl#> \
      PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
      SELECT ?class ?label \
      WHERE { { ?property rdfs:domain <' + str(c[0]) + '> OPTIONAL { ?property rdfs:label ?label } } \
      UNION { ?property rdfs:domain <' + str(c[0]) + '> OPTIONAL { ?property rdfs:label ?label } } } \
      ORDER BY ?label')
    for p in rs2:
      print p
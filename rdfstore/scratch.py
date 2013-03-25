'''
Created on Mar 11, 2013

@author: howard
'''

from rdflib import ConjunctiveGraph, Graph, plugin
from rdflib.store import Store, VALID_STORE
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib import RDFS, RDF, OWL, XSD

from api import BASE_GRAPH_URI, SCHEMA_GRAPH_URI, DATABASE_STORE, _get_db_config_string


store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')

rt = store.open(_get_db_config_string(), create=False)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef(BASE_GRAPH_URI))

sg = Graph(store, identifier=URIRef(SCHEMA_GRAPH_URI))
g = sg


# query for all classes
#
rs = g.query(
  'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
   PREFIX owl: <http://www.w3.org/2002/07/owl#> \
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
   PREFIX sg: <http://example.com/rdf/schemas/> \
   SELECT ?class \
   WHERE { { ?class rdf:type owl:Class . OPTIONAL { ?class rdfs:label ?label } } \
   UNION { ?class rdf:type rdfs:Class . OPTIONAL { ?class rdfs:label ?label } } } \
   ORDER BY ?label')


# query for all primary classes
#
rs = g.query(
  'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
   PREFIX owl: <http://www.w3.org/2002/07/owl#> \
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
   PREFIX sg: <http://example.com/rdf/schemas/> \
   SELECT ?class \
   WHERE { ?class rdf:type owl:Class . ?class sg:isUsedFor "primary" OPTIONAL { ?class rdfs:label ?label } } \
   ORDER BY ?label')
    
    
# query schema related to class
#
classUri = 'http://example.com/rdf/schemas/Collectable'
classUriRef = URIRef(classUri)

rs = g.query(
 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
  PREFIX owl: <http://www.w3.org/2002/07/owl#> \
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
  PREFIX sg: <http://example.com/rdf/schemas/> \
  SELECT ?property ?label ?type ?range ?order \
  WHERE { \
    { ?property rdfs:domain <' + str(classUriRef) + '> ; \
                rdfs:label ?label ;\
                sg:displayOrder ?order ; \
                rdf:type ?type \
      OPTIONAL { ?property rdfs:range ?range } \
      FILTER (STRSTARTS(STR(?type), STR(owl:DatatypeProperty)) || \
              STRSTARTS(STR(?type), STR(owl:ObjectProperty)) || \
              STRSTARTS(STR(?type), STR(rdf:Property))) \
    } \
  } \
  ORDER BY ?order')


#
# query for all subjects, titles, descriptions, and acquire prices
#
rs = ug.query(
 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
  PREFIX dc: <http://purl.org/dc/elements/1.1/> \
  PREFIX sg: <http://example.com/rdf/schemas/> \
  SELECT ?subject ?class ?createTime ?title ?description ?acquirePrice \
  WHERE { \
    ?subject rdf:type ?class ; \
             sg:createTime ?createTime \
    OPTIONAL { ?subject dc:title ?title } \
    OPTIONAL { ?subject dc:description ?description } \
    OPTIONAL { ?subject sg:acquirePrice ?acquirePrice } \
    FILTER (STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Collectable") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Basket") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/CarvedStone") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Doll") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Mask") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Pipe") || STRSTARTS(STR(?class), "http://example.com/rdf/schemas/Rug")) \
  } \
  ORDER BY ?createTime')

rs = ug.query(
 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
  PREFIX owl: <http://www.w3.org/2002/07/owl#> \
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
  PREFIX sg: <http://example.com/rdf/schemas/> \
  SELECT ?subject ?createTime ?title ?description ?acquirePrice \
  WHERE { \
    ?subject rdf:type ?class \
  } \
  ORDER BY ?createTime')

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
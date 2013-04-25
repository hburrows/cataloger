'''
Created on Mar 11, 2013

@author: howard
'''

from rdflib import ConjunctiveGraph, Graph, plugin
from rdflib.store import Store, VALID_STORE
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDFS, RDF, OWL, XSD

from api import BASE_GRAPH_URI, SCHEMA_GRAPH_URI, USER_GRAPH_URI, DATABASE_STORE, _get_db_config_string

import rdflib_sparql
from rdflib_sparql.processor import processUpdate
rdflib_sparql.SPARQL_LOAD_GRAPHS = False

SCHEMA = Namespace(SCHEMA_GRAPH_URI)

store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')

rt = store.open(_get_db_config_string(), create=False)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef(BASE_GRAPH_URI))

sg = Graph(store, identifier=URIRef(SCHEMA_GRAPH_URI))
g = sg

USER = Namespace(str(USER_GRAPH_URI).format(userId=2))
ug = Graph(store, identifier=URIRef(USER))

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

# using named graphs
template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX sg: <{sg}>
SELECT ?class ?label ?comment
FROM NAMED <{sg}>
WHERE {{
  GRAPH <{sg}>
  {{
    {{ 
      ?class rdf:type owl:Class .
      ?class sg:isUsedFor "primary" 
      OPTIONAL {{ ?class rdfs:label ?label . }}
      OPTIONAL {{ ?class rdfs:comment ?comment . }}
    }}
    UNION
    {{
      ?class rdf:type rdfs:Class .
      ?class sg:isUsedFor "primary" 
      OPTIONAL {{ ?class rdfs:label ?label . }}
      OPTIONAL {{ ?class rdfs:comment ?comment . }}
    }}
  }}
}}
ORDER BY (?label)
'''

rq = template.format(sg='http://example.com/rdf/schemas/')
print rq

for cls, l, comment in citg.query(rq):
  print l, ' - ', comment, ' (', cls, ')'


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

# query seq for elements
template = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?seq_index ?seq_item ?type WHERE {{
     <{0}> ?seq_index ?seq_item .
     ?seq_item rdf:type <{1}> .
}}
"""
query = template.format('N882eb3fad4e24e05a903122b7a535cf0', 'http://purl.org/dc/dcmitype/StillImage')

for idx, elNode, elType in ug.query(query):
  print idx, elNode, elType


# query the media's still-image subjects for thumbnails.
template = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ug: <http://example.com/rdf/users/2#>
PREFIX sg: <http://example.com/rdf/schemas/>
SELECT ?seq_index ?media_item ?type ?stillImageType ?stillImageURL
WHERE {{
     <{0}> ?seq_index ?media_item .
     ?media_item rdf:type <{1}> .
     ?media_item sg:images ?media_item_seq .
     ?media_item_seq ?media_item_seq_index ?media_item_instance .
     ?media_item_instance sg:stillImageType "thumbnail" .
     ?media_item_instance sg:stillImageURL ?stillImageURL .
}}
"""
query = template.format('Nf8afb396966049fd8db7ffa930f816ee', 'http://example.com/rdf/schemas/StillImage')

for idx, elNode, elType, imgType, imgUrl in ug.query(query):
  print idx, elNode, elType, imgType, imgUrl

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

import rdflib_sparql
rdflib_sparql.SPARQL_LOAD_GRAPHS = False

#
# Get all subclasses of Entry
#
template = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?s ?typeLabel ?e
FROM NAMED <{ug}>
FROM NAMED <{sg}>
WHERE {{
     ?s rdfs:subClassOf+ <{type}> .
     ?s rdfs:label ?typeLabel .
     ?e rdf:type ?s .
}}
"""

query = template.format(type=SCHEMA['Entry'], ug=USER, sg=SCHEMA)

print query

for s, type_label, e in citg.query(query):
  print s, ', ', type_label, ', ', e


#
#  query all graphs
#
query = '''
SELECT DISTINCT ?g 
WHERE
{
  GRAPH ?g {?s ?p ?o }
}
'''
  
for g in citg.query(query):
  print g

#
#  query all triples
#
template = '''
SELECT ?s ?p ?o
WHERE
{{
  ?s ?p ?o
}}
'''
  
#
#  query all triples in named graph
#
template = '''
SELECT ?s ?p ?o
FROM NAMED <{ug}> 
WHERE
{{
  GRAPH <{ug}> {{ ?s ?p ?o }}
}}
'''

rq = template.format(ug=USER, sg=SCHEMA)

for s, p, o in citg.query(rq):
  print s, p, o


#
# Query all user entries of a type or subclass of type
#
template = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?s ?typeLabel
FROM NAMED <{ug}>
FROM NAMED <{sg}>
WHERE {{
  GRAPH <{sg}> {{
    ?s rdfs:subClassOf+ <{type}> .
    ?s rdfs:label ?typeLabel .
  }}
  GRAPH <{ug}> {{
    ?e rdf:type ?s .
  }}
}}
"""

template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <{ug}>
SELECT ?p ?o
FROM NAMED <{ug}>
FROM NAMED <{sg}>
WHERE {{
  GRAPH <{ug}> {{
    <{subject}> ?p ?o. 
  }}
}}
'''

query = template.format(subject='http://example.com/rdf/users/2/3'.format(str(USER)), ug=USER, sg=SCHEMA)

print query

for p, o in citg.query(query):
  print p, ', ', o




template = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sg: <{sg}>
PREFIX : <{ug}>
SELECT ?s ?type ?createTime ?title ?description ?acquirePrice ?thumbnailURL ?typeLabel
FROM NAMED <{ug}>
FROM NAMED <{sg}>
WHERE {{
  {{
    GRAPH <{ug}> {{
      ?s rdf:type ?type .
       GRAPH <{sg}> {{
         ?type rdfs:label ?typeLabel .
       }}
       FILTER(?type IN (<{type}>))
    }}
  }}
  UNION
  {{
    GRAPH <{sg}> {{
      ?type rdfs:subClassOf+ <{type}> .
      ?type rdfs:label ?typeLabel .
    }}
  }}
  GRAPH <{ug}> {{
    ?s rdf:type ?type .
    ?s sg:createTime ?createTime .
    OPTIONAL {{ ?s dc:title ?title }}             
    OPTIONAL {{ ?s dc:description ?description }}             
    OPTIONAL {{ ?s sg:acquirePrice ?acquirePrice }}
    OPTIONAL {{ ?s sg:acquirePrice ?acquirePrice }}
    OPTIONAL {{
      # get the thumbnail image for the first StillImage media object
      ?s sg:media ?media .
      ?media ?seq_index ?media_item .
      ?media_item rdf:type sg:StillImage .
      ?media_item sg:images ?media_item_seq .
      ?media_item_seq ?media_item_seq_index ?media_item_instance .
      ?media_item_instance sg:stillImageType "thumbnail" .
      ?media_item_instance sg:stillImageURL ?thumbnailURL .
    }}      
  }}
}}
ORDER BY ?createTime
"""

query = template.format(type=SCHEMA['Collectable'], ug=USER, sg=SCHEMA)

print query

for s, type, createTime, title, description, acquirePrice, thumbnail, type_label in citg.query(query):
  print s, ', ', type, ', ', createTime, ', ', type_label, ', ', title, ', ', description, ', ', acquirePrice, ', ', thumbnail


#
#  Get all graphs
#
rq = '''
SELECT ?g 
WHERE
{ 
  GRAPH ?g {}
}
'''
for g in citg.query(rq):
  print g


#
# dump all triples in the named graph
#
template = '''
PREFIX : <{ug}>
SELECT ?s ?p ?o
FROM NAMED <{ug}> 
WHERE
{{
  GRAPH : {{ ?s ?p ?o }}
}}
'''

rq = template.format(ug=TEST, sg=SCHEMA)

for s, p, o in citg.query(rq):
  print s, p, o

#
# Load schemas into named graph
#
#
ru = '''
PREFIX sg: <http://example.com/rdf/schemas/>
# rdf and rdfs
LOAD <http://www.w3.org/2000/01/rdf-schema> ;
LOAD <http://www.w3.org/1999/02/22-rdf-syntax-ns> ;
# owl
LOAD <http://www.w3.org/2002/07/owl> ;
# ordered list ontology
LOAD <http://purl.org/ontology/olo/core> ;
# dublin core stuff
LOAD <http://purl.org/dc/elements/1.1/> ;
LOAD <http://purl.org/dc/terms/> ;
LOAD <http://purl.org/dc/dcmitype/> ;
'''

# clear the named graph
#
template = '''
PREFIX : <{ug}>
CLEAR GRAPH :
'''
ru = template.format(ug=USER, sg=SCHEMA)
processUpdate(citg,ru)


#
# Insert triples into the named graph
#
template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX : <{ug}>

INSERT DATA {{
  GRAPH : {{
    :howard dc:title "Howard Burrows" .
    :howard :friends [
      a rdf:Seq ;
      rdf:_1 "Dan" ;
      rdf:_2 "Scott" ;
      rdf:_3 "Jane"
    ] .
  }}
}}
'''
  
template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sg: <{sg}>
PREFIX : <{ug}>

INSERT DATA {{
  GRAPH : {{
    :dan dc:title "Dan Rael" .
    :dan :friends [ 
      a rdf:Seq ;
      rdf:_1 "Howard" ;
      rdf:_2 "Butters" ;
      rdf:_3 "Zuni"
    ] .
   :dan :books [
      a rdf:Seq ;
      rdf:_1 "Guns, Germs, and Steel" ;
      rdf:_2 "1491"
   ] .
 }}
}}
'''
  
ru = template.format(ug=USER, sg=SCHEMA)

processUpdate(citg,ru)

template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sg: <{sg}>
PREFIX : <{ug}>

DELETE WHERE {{
  :dan ?p ?o .
}}
'''
  
ru = template.format(ug=USER, sg=SCHEMA)

processUpdate(ug,ru)

template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sg: <{sg}>
PREFIX : <{ug}>
SELECT ?p ?o
FROM NAMED <{ug}>
WHERE
{{
 GRAPH <{ug}>
 {{
   :dan :friends ?seq .
   ?seq ?p ?o .
 }}
}}
'''

rq = template.format(ug=USER, sg=SCHEMA)

for p, o in citg.query(rq):
  print p, o
g = citg


ru = '''
PREFIX : <http://example.com/rdf/users/2/>
INSERT DATA {
  GRAPH : {
    <http://example.com/rdf/users/2/29> <http://purl.org/dc/elements/1.1/title> "test title" . 
    <http://example.com/rdf/users/2/29> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/rdf/schemas/Doll> . 
    <http://example.com/rdf/users/2/29> <http://purl.org/dc/elements/1.1/description> "test description" . 
    <http://example.com/rdf/users/2/29> <http://example.com/rdf/schemas/media> [ 
      <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq> ; 
      <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> [ 
        <http://example.com/rdf/schemas/location> [ 
          <http://www.w3.org/2003/01/geo/wgs84_pos#lat> 0 ; 
          <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2003/01/geo/wgs84_pos#Point> ; 
          <http://www.w3.org/2003/01/geo/wgs84_pos#long> 0 ;
        ] ; 
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/rdf/schemas/StillImage> ; 
        <http://example.com/rdf/schemas/images> [ 
          <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq> ; 
          <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> [ 
            <http://example.com/rdf/schemas/stillImageWidth> 478 ; 
            <http://example.com/rdf/schemas/stillImageHeight> 640 ; 
            <http://example.com/rdf/schemas/stillImageType> "original" ; 
            <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/dc/dcmitype/StillImage> ; 
            <http://example.com/rdf/schemas/stillImageURL> "http://images.catalogit.howardburrows.com.s3.amazonaws.com/users/2/a6bef60.original.jpeg" ;
          ] ; 
          <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> [ 
            <http://example.com/rdf/schemas/stillImageWidth> 45 ;   
            <http://example.com/rdf/schemas/stillImageHeight> 60 ; 
            <http://example.com/rdf/schemas/stillImageType> "thumbnail" ; 
            <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/dc/dcmitype/StillImage> ; 
            <http://example.com/rdf/schemas/stillImageURL> "http://images.catalogit.howardburrows.com.s3.amazonaws.com/users/2/a6bef60.thumbnail.jpeg" 
          ]
        ]
      ]
    ] .
  }
}
'''

processUpdate(citg,ru)

ru = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX : <http://example.com/rdf/test/>

INSERT DATA {
  GRAPH : {
    :dan dc:title "Dan Rael" .
    :dan :friends [ 
      a rdf:Seq ;
      rdf:_1 "Howard" ;
      rdf:_2 "Cary" ;
      rdf:_3 "Jill"
    ] .
   :dan :numbers [
      a rdf:Seq ;
      rdf:_1 [ rdfs:label "Home" ;
               :number "123-456-7890" ] ;
      rdf:_2 [ rdfs:label "Work" ;
               :number "123-654-0987" ] ;
   ] .
 }
}
'''

processUpdate(citg,ru)



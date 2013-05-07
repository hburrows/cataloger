import urllib
from time import time

from django.conf import settings

from rdflib import Namespace

from SPARQLWrapper import SPARQLWrapper, JSON

import requests

from api import SCHEMA_GRAPH_URI


SCHEMA = Namespace(SCHEMA_GRAPH_URI)

'''
  UTILITY
'''

def get_full_json(graphURI, uriRef, label, comment):

  # create a list of properties

  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <{sg}>
SELECT ?property ?label ?range ?type ?comment ?embed
WHERE
{{
  GRAPH <{sg}>
  {{
    ?property rdfs:domain <{domain}> ;
              rdf:type ?type .
    OPTIONAL {{ ?property rdfs:range ?range . }}
    OPTIONAL {{ ?property rdfs:label ?label . }}
    OPTIONAL {{ ?property rdfs:comment ?comment . }}
    OPTIONAL {{ ?property :displayOrder ?order . }}
    OPTIONAL {{ ?property :embed ?embed . }}
    FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property)) 
  }}
}}
ORDER BY (?order)'''

  rq = template.format(domain=uriRef, sg=graphURI)

#  t0 = time()

  properties = []
  #for cls, label, prop_range, prop_type, comment in g.query(rq):
  for result in sparql_query(rq)["results"]["bindings"]:

    properties.append({
      'property': result['property']['value'],
      'label': result['label']['value'] if 'label' in result else None,
      'range': result['range']['value'] if 'range' in result else None,
      'type': result['type']['value'],
      'comment': result['comment']['value'] if 'comment' in result else None,
      'embed': result['embed']['value'] if 'embed' in result else False
    })

#   t1 = time()
#   print(str(t1 - t0))

  result = {
    'id': uriRef,
    'name': label,
    'comment': comment,
    'properties': properties }
  
#   t2 = time()
#   print(str(t2 - t1))

  return result

def get_base_json(graphURI, uriRef, label, comment):

  # create a list of properties
  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?property ?range ?type
FROM NAMED <{sg}>
WHERE
{{
  GRAPH <{sg}>
  {{
    ?property rdfs:domain <{domain}> ;
              rdf:type ?type
    OPTIONAL {{ ?property rdfs:range ?range }}
    FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property)) 
  }}
}}'''

  rq = template.format(domain=str(uriRef), sg=graphURI)

  properties = []
  for result in sparql_query(rq)["results"]["bindings"]:

    properties.append({
      'property': result['property']['value'],
      'range': result['range']['value'] if 'range' in result else None,
      'type': result['type']['value'],
    })

  return {
    'id': str(uriRef),
    'properties': properties }


# output everything about the super classes
def dump_supers(graphURI, subURI, l, formatter):

  rq_tmpl = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <{graph_uri}>
SELECT ?super ?label ?comment
WHERE {{
  GRAPH :
  {{
     ?super ^rdfs:subClassOf+ <{sub_uri}>
     OPTIONAL {{ ?super rdfs:label ?label }}
     OPTIONAL {{ ?super rdfs:comment ?comment }}
  }}
}}
'''
  rq = rq_tmpl.format(graph_uri=graphURI, sub_uri=subURI)
  
  for result in sparql_query(rq)["results"]["bindings"]:

    superURI = result['super']['value']
    label = result['label']['value'] if 'label' in result else None
    comment = result['comment']['value'] if 'comment' in result else None
  
    l.append(formatter(graphURI, superURI, label, comment))
    dump_supers(graphURI, superURI, l, formatter)


def get_class_info(classURI):

  rq_tmpl = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <{graph_uri}>
SELECT ?label ?comment
WHERE {{
  GRAPH :
  {{
     OPTIONAL {{ <{class_uri}> rdfs:label ?label }}
     OPTIONAL {{ <{class_uri}> rdfs:comment ?comment }}
  }}
}}
'''
  rq = rq_tmpl.format(graph_uri=SCHEMA_GRAPH_URI, class_uri=classURI)

  results = sparql_query(rq)
  if len(results["results"]["bindings"]) > 0:
    result = results["results"]["bindings"][0]
    label = result['label']['value'] if 'label' in result else None    
    comment = result['comment']['value'] if 'comment' in result else None
  else:
    label = None
    comment = None
    
  return label, comment


def get_full_schema_for(classURI):
  print "Getting full schema for ", classURI

  label, comment = get_class_info(classURI)
      
  classDefs = []
  classDefs.append(get_full_json(SCHEMA_GRAPH_URI, classURI, label, comment))
  dump_supers(SCHEMA_GRAPH_URI, classURI, classDefs, get_full_json)

  # reverse result and return
  return classDefs[::-1];


def get_base_schema_for(classURI):
  label, comment = get_class_info(classURI)
      
  classDefs = []
  classDefs.append(get_base_json(SCHEMA_GRAPH_URI, classURI, label, comment))
  dump_supers(SCHEMA_GRAPH_URI, classURI, classDefs, get_base_json)

  flatProperties = []
  for classDef in classDefs:
    flatProperties.extend(classDef['properties'])
  
  return flatProperties

def get_schema_and_lookup_for(classURI):
  label, comment = get_class_info(classURI)
      
  classDefs = []
  classDefs.append(get_base_json(SCHEMA_GRAPH_URI, classURI, label, comment))
  dump_supers(SCHEMA_GRAPH_URI, classURI, classDefs, get_base_json)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return classDefs[::-1], lookup

def get_full_schema_and_lookup_for(classURI):
  label, comment = get_class_info(classURI)
      
  classDefs = []
  classDefs.append(get_full_json(SCHEMA_GRAPH_URI, classURI, label, comment))
  dump_supers(SCHEMA_GRAPH_URI, classURI, classDefs, get_full_json)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return classDefs[::-1], lookup

def sparql_query (rq):
  sparql = SPARQLWrapper(settings.SPARQL_QUERY_ENDPOINT)              
  sparql.setQuery(rq)
  sparql.setReturnFormat(JSON)
  
  return sparql.query().convert()

def sparql_update (ru):
  r = requests.post(settings.SPARQL_UPDATE_ENDPOINT,data={'update': ru})
  if r.status_code != 200:
    raise Exception('Error issuing sparql update: {0}'.format(r.status_code))

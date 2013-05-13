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

def sparql_froms_for_user(user):
  return ' '.join(['FROM <' + g.graph_uri + '>' for g in user.userprofile.graphs.all()])

def get_full_json(graphs, uriRef, label, comment):

  # create a list of properties

  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX common: <{common}>
SELECT ?property ?label ?range ?type ?comment ?embed
{graphs}
WHERE
{{
  ?property rdfs:domain <{domain}> ;
            rdf:type ?type .
  OPTIONAL {{ ?property rdfs:range ?range . }}
  OPTIONAL {{ ?property rdfs:label ?label . }}
  OPTIONAL {{ ?property rdfs:comment ?comment . }}
  OPTIONAL {{ ?property common:displayOrder ?order . }}
  OPTIONAL {{ ?property common:embed ?embed . }}
  FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property)) 
}}
ORDER BY (?order)'''

  rq = template.format(graphs=graphs, common=SCHEMA_GRAPH_URI, domain=uriRef)

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

def get_base_json(graphs, uriRef, label, comment):

  # create a list of properties
  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX common: <{common}>
SELECT ?property ?range ?type
{graphs}
WHERE
{{
  ?property rdfs:domain <{domain}> ;
            rdf:type ?type
  OPTIONAL {{ ?property rdfs:range ?range }}
  OPTIONAL {{ ?property common:embed ?embed . }}
  FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property)) 
}}'''

  rq = template.format(graphs=graphs, common=SCHEMA_GRAPH_URI, domain=uriRef)

  properties = []
  for result in sparql_query(rq)["results"]["bindings"]:

    properties.append({
      'property': result['property']['value'],
      'range': result['range']['value'] if 'range' in result else None,
      'type': result['type']['value'],
      'embed': result['embed']['value'] if 'embed' in result else False
    })

  return {
    'id': str(uriRef),
    'properties': properties }


# output everything about the super classes
def dump_supers(graphs, subURI, l, formatter):

  rq_tmpl = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?s ?super ?label ?comment
{graphs}
{{
  <{sub_uri}> rdfs:subClassOf ?super
  OPTIONAL {{ ?super rdfs:label ?label }}
  OPTIONAL {{ ?super rdfs:comment ?comment }}
}}
'''
  rq = rq_tmpl.format(graphs=graphs, sub_uri=subURI)
  
  supers = set([])
  for result in sparql_query(rq)["results"]["bindings"]:

    superURI = result['super']['value']
    label = result['label']['value'] if 'label' in result else None
    comment = result['comment']['value'] if 'comment' in result else None

    if superURI in supers:
      continue

    meta = formatter(graphs, superURI, label, comment)
    
    supers.add(superURI)

    l.append(meta)

    dump_supers(graphs, superURI, l, formatter)


def get_class_info(graphs, classURI):

  rq_tmpl = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?label ?comment
{graphs}
WHERE {{
  OPTIONAL {{ <{class_uri}> rdfs:label ?label }}
  OPTIONAL {{ <{class_uri}> rdfs:comment ?comment }}
}}
'''
  rq = rq_tmpl.format(graphs=graphs, class_uri=classURI)

  results = sparql_query(rq)
  if len(results["results"]["bindings"]) > 0:
    result = results["results"]["bindings"][0]
    label = result['label']['value'] if 'label' in result else None    
    comment = result['comment']['value'] if 'comment' in result else None
  else:
    label = None
    comment = None
    
  return label, comment


def get_full_schema_for(graphs, classURI):
  print "Getting full schema for ", classURI

  label, comment = get_class_info(graphs, classURI)
      
  classDefs = []
  classDefs.append(get_full_json(graphs, classURI, label, comment))
  dump_supers(graphs, classURI, classDefs, get_full_json)

  # reverse result and return
  return classDefs[::-1];

def get_base_schema_for(graphs, classURI):
  label, comment = get_class_info(graphs, classURI)
      
  classDefs = []
  classDefs.append(get_base_json(graphs, classURI, label, comment))
  dump_supers(graphs, classURI, classDefs, get_base_json)

  flatProperties = []
  for classDef in classDefs:
    flatProperties.extend(classDef['properties'])
  
  return flatProperties

def get_schema_and_lookup_for(graphs, classURI):
  label, comment = get_class_info(graphs, classURI)
      
  classDefs = []
  classDefs.append(get_base_json(graphs, classURI, label, comment))
  dump_supers(graphs, classURI, classDefs, get_base_json)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return classDefs[::-1], lookup

def get_full_schema_and_lookup_for(graphs, classURI):
  label, comment = get_class_info(graphs, classURI)
      
  classDefs = []
  classDefs.append(get_full_json(graphs, classURI, label, comment))
  dump_supers(graphs, classURI, classDefs, get_full_json)

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

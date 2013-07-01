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

def sparql_graphs_for_user(user):
  return ','.join(['<' + g.graph_uri + '>' for g in user.userprofile.graphs.all()])
  
def get_full_json(graphs, uriRef, label, comment):

  # TODO: this would be much cleaner with FROM but can't get it to work with jena and sdb

  # create a list of properties

  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX common: <{common}>
SELECT ?property ?label ?range ?type ?comment ?embed ?bnode ?enum 
{{
  # get all properties for the class based on 'domain' relationship
  {{
    GRAPH ?g1 {{
      ?property rdfs:domain <{domain}>
    }}
   FILTER (?g1 IN ({graphs}))
  }}
  # the actual property definitions might be in a different graph
  # so need to use a different active graph
  GRAPH ?g2 {{
    ?property rdf:type ?type .
    OPTIONAL {{ ?property rdfs:range ?range . }}
    OPTIONAL {{ ?property rdfs:label ?label . }}
    OPTIONAL {{ ?property rdfs:comment ?comment . }}
    OPTIONAL {{ ?property common:displayOrder ?order . }}
    OPTIONAL {{ ?property common:embed ?embed . }}
    OPTIONAL {{ ?property common:bnode ?bnode . }}
    OPTIONAL {{ ?property common:enumeration ?enum }}
    FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property))
  }}
  FILTER (?g2 IN ({graphs}))
}}
ORDER BY (?order)'''

  rq = template.format(graphs=graphs, common=SCHEMA_GRAPH_URI, domain=uriRef)

#  t0 = time()

  properties = []
  #for cls, label, prop_range, prop_type, comment in g.query(rq):
  for result in sparql_query(rq)["results"]["bindings"]:

    propertyId = result['property']['value']

    propertyDict = {
      'property': propertyId,
      'label': result['label']['value'] if 'label' in result else None,
      'range': result['range']['value'] if 'range' in result else None,
      'type': result['type']['value'],
      'comment': result['comment']['value'] if 'comment' in result else None
    }

    if 'embed' in result:
      propertyDict['embed'] = result['embed']['value']

    if 'bnode' in result:
      propertyDict['bnode'] = result['bnode']['value']

    if 'enum' in result:
      template = '''
PREFIX common: <{common}>
SELECT ?idx ?value
WHERE
{{
  GRAPH ?g {{
    <{property}> common:enumeration [ ?idx ?value ] ;
  }}
  FILTER (?g IN ({graphs}))
}}'''

      rq = template.format(graphs=graphs, common=SCHEMA_GRAPH_URI, property=propertyId)

      enumerations = []
      for distinctValue in sparql_query(rq)["results"]["bindings"]:
        enumerations.append(distinctValue['value']['value'])
      
      propertyDict['oneOf'] = enumerations

    properties.append(propertyDict)

  result = {
    'id': uriRef,
    'name': label,
    'comment': comment,
    'properties': properties }
  
  return result

def get_base_json(graphs, uriRef, label, comment):

  # TODO: would be better with SPARQL FROM but can't get it to work with jena and sdb
  
  # create a list of properties
  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX common: <{common}>
SELECT ?property ?range ?type
WHERE
{{
  # get all properties for the class based on 'domain' relationship
  {{
    GRAPH ?g1 {{
      ?property rdfs:domain <{domain}>
    }}
    FILTER (?g1 IN ({graphs}))
  }}
  # the actual property definitions might be in a different graph
  # so need to use a different active graph
  GRAPH ?g2 {{
    ?property rdf:type ?type
    OPTIONAL {{ ?property rdfs:range ?range }}
    FILTER (?type IN (owl:DatatypeProperty, owl:ObjectProperty, rdf:Seq, rdf:Property))
  }}
  FILTER (?g2 IN ({graphs}))
}}'''

  rq = template.format(graphs=graphs, common=SCHEMA_GRAPH_URI, domain=uriRef)

  properties = []
  for result in sparql_query(rq)["results"]["bindings"]:

    properties.append({
      'property': result['property']['value'],
      'range': result['range']['value'] if 'range' in result else None,
      'type': result['type']['value']
    })

  return {
    'id': str(uriRef),
    'properties': properties }


# output everything about the super classes
def dump_supers(graphs, subURI, l, formatter):

  # TODO: Using SPARQL FROM would probably work better but can't get it to work with Jena and sdb
  
  rq_tmpl = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?super ?label ?comment
{{
  {{
    # get super class information
    GRAPH ?g {{
      <{sub_uri}> rdfs:subClassOf ?super
    }}
    FILTER (?g IN ({graphs}))
  }}
  # query for super class information in any graph since it's not
  # not necessarily in the active graph
  GRAPH ?g2 {{
    ?super rdf:type ?t
    OPTIONAL {{ ?super rdfs:label ?label }}
    OPTIONAL {{ ?super rdfs:comment ?comment }}
  }}
  FILTER (?g2 IN ({graphs}))
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
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?label ?comment ?t
WHERE {{
  GRAPH ?g {{
    <{class_uri}> rdf:type ?t
    OPTIONAL {{ <{class_uri}> rdfs:label ?label }}
    OPTIONAL {{ <{class_uri}> rdfs:comment ?comment }}
  }}
  FILTER (?g IN ({graphs}))
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
  
  print "Getting full schema for " + classURI

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

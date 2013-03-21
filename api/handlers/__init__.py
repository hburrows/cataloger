from rdflib import URIRef
from rdflib import OWL, RDFS

BASE_GRAPH_URI = "http://example.com/rdf/"

SCHEMA_GRAPH_URI = BASE_GRAPH_URI + 'schemas/'

USER_GRAPH_URI = BASE_GRAPH_URI + 'users/{userId}#'

MYSQL_HOST = 'localhost'
POSTGRES_HOST = '/tmp/'
USER = 'howard'
PASSWORD = 'd#vel0p'
DB = 'rdfstore'

'''
  DATABASE
'''
def _get_mysql_config_string():
  return 'host={0},user={1},password={2},db={3}'.format(MYSQL_HOST, USER, PASSWORD, DB)

def _get_postgresql_config_string():
  return 'host={0} user={1} dbname={2}'.format(POSTGRES_HOST, USER, DB)

_get_db_config_string = _get_postgresql_config_string

'''
  UTILITY
'''

def get_base_json(g, uriRef):
  # create a list of properties
  rs = g.query(' \
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
    PREFIX owl: <http://www.w3.org/2002/07/owl#> \
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
    SELECT ?property ?range ?type \
    WHERE { \
            { ?property rdfs:domain <' + str(uriRef) + '> \
              OPTIONAL { ?property rdfs:range ?range } \
              OPTIONAL { ?property rdf:type ?type } \
              FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#ObjectProperty")) \
            } \
            UNION \
            { ?property rdfs:domain <' + str(uriRef) + '> \
              OPTIONAL { ?property rdfs:range ?range } \
              OPTIONAL { ?property rdf:type ?type } \
              FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#DatatypeProperty")) \
            } \
          } \
    ORDER BY ?label')  
  properties = []
  for prop in rs:

    properties.append({
      'property': prop[0],
      'range': prop[1],
      'type': prop[2],
    })

  return {
    'classUri': str(uriRef),
    'properties': properties }


# output everything about my superclasses
def dump_supers(g, subUR, l):
  for superUR in g.objects(subUR, RDFS['subClassOf']): 
    l.append(get_base_json(g, superUR))
    dump_supers(g, superUR, l)

def get_schema_for(g, classURIRef):
  classDefs = []
  classDefs.append(get_base_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs)

  flatProperties = []
  for classDef in classDefs:
    flatProperties.extend(classDef['properties'])
  
  return flatProperties

def get_predicate_lookup_for(g, classURIRef):
  classDefs = []
  classDefs.append(get_base_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return lookup
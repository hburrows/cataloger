import urllib

from rdflib import URIRef, Namespace
from rdflib import OWL, RDFS

from api import SCHEMA_GRAPH_URI

'''
  CONSTANTS
'''

SCHEMA = Namespace(SCHEMA_GRAPH_URI)

DCMI = Namespace('http://purl.org/dc/dcmitype/')
GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')


'''
  UTILITY
'''

def get_ancestors(g, classUriRef, ancestors):
  if not classUriRef:
    return False

  for a in g.objects(classUriRef, RDFS['subClassOf']):
    ancestors.append(str(a))
    get_ancestors(g, a, ancestors)

  return

def get_full_json(g, uriRef):

  # create a list of properties
  rs = g.query(
   'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
    PREFIX owl: <http://www.w3.org/2002/07/owl#> \
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
    PREFIX sg: <http://example.com/rdf/schemas/> \
    SELECT ?property ?label ?range ?type ?order \
    WHERE { \
      { ?property rdfs:domain <' + str(uriRef) + '> ; \
                  rdfs:label ?label ;\
                  sg:displayOrder ?order ; \
                  rdf:type ?type \
        OPTIONAL { ?property rdfs:range ?range } \
        FILTER (STRSTARTS(STR(?type), STR(owl:DatatypeProperty)) || \
                STRSTARTS(STR(?type), STR(owl:ObjectProperty)) || \
                STRSTARTS(STR(?type), STR(rdf:Seq)) || \
                STRSTARTS(STR(?type), STR(rdf:Property))) \
      } \
    } \
    ORDER BY ?order')

  properties = []
  for prop in rs:

    # get the labels
    l = g.preferredLabel(prop[0])
    
    # get the comment
    comment = g.comment(prop[0])
    if not comment:
      comments = list(g.objects(prop[0], URIRef('http://www.w3.org/2000/01/rdf-schema#comment')))
      comment = comments[0] if len(comments) > 0 else None
      
    # get a list of all my ancestors (that which the property is a subclass of).  Only do
    # this for "object" type properties for performance reasons
    ancestors = []
    if prop[3] == URIRef(OWL['ObjectProperty']):
      get_ancestors(g, prop[2], ancestors)

    properties.append({
      'property': prop[0],
      'label': l[0][1] if len(l) > 0 else '',
      'range': prop[2],
      'type': prop[3],
      'comment': comment,
      'ancestors': ancestors
    })

  l = g.preferredLabel(uriRef)
  
  return {
    'id': uriRef,
    'name': l[0][1] if len(l) > 0 else '',
    'comment': g.comment(uriRef),
    'properties': properties }

def get_base_json(g, uriRef):
  # create a list of properties
  rs = g.query(
   'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
    PREFIX owl: <http://www.w3.org/2002/07/owl#> \
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
    PREFIX sg: <http://example.com/rdf/schemas/> \
    SELECT ?property ?range ?type \
    WHERE { \
      { ?property rdfs:domain <' + str(uriRef) + '> ; \
                  rdf:type ?type \
        OPTIONAL { ?property rdfs:range ?range } \
        FILTER (STRSTARTS(STR(?type), STR(owl:DatatypeProperty)) || \
                STRSTARTS(STR(?type), STR(owl:ObjectProperty)) || \
                STRSTARTS(STR(?type), STR(rdf:Seq)) || \
                STRSTARTS(STR(?type), STR(rdf:Property))) \
      } \
    }')
  properties = []
  for prop in rs:

    properties.append({
      'property': prop[0],
      'range': prop[1],
      'type': prop[2],
    })

  return {
    'id': str(uriRef),
    'properties': properties }


# output everything about the super classes
def dump_supers(g, subUR, l, formatter):
  for superUR in g.objects(subUR, RDFS['subClassOf']): 
    l.append(formatter(g, superUR))
    dump_supers(g, superUR, l, formatter)

def get_full_schema_for(classURIRef, g):
  print "Getting full schema for ", str(classURIRef)
  classDefs = []
  classDefs.append(get_full_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs, get_full_json)

  # reverse result and return
  return classDefs[::-1];

def get_base_schema_for(g, classURIRef):
  classDefs = []
  classDefs.append(get_base_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs, get_base_json)

  flatProperties = []
  for classDef in classDefs:
    flatProperties.extend(classDef['properties'])
  
  return flatProperties

def get_schema_and_lookup_for(g, classURIRef):
  classDefs = []
  classDefs.append(get_base_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs, get_base_json)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return classDefs[::-1], lookup

def get_full_schema_and_lookup_for(g, classURIRef):
  classDefs = []
  classDefs.append(get_full_json(g, classURIRef))
  dump_supers(g, classURIRef, classDefs, get_full_json)

  lookup = {}
  for classDef in classDefs:
    for predicate in classDef['properties']:
      lookup[str(predicate['property'])] = predicate
  
  return classDefs[::-1], lookup
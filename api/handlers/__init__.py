from rdflib import URIRef
from rdflib import OWL, RDFS

'''
  UTILITY
'''

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
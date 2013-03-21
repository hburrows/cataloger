'''
Created on Mar 8, 2013

@author: howard
'''

from piston.handler import BaseHandler

from rdflib import ConjunctiveGraph, URIRef, Graph
from rdflib.store import VALID_STORE
from rdflib import RDFS, OWL

import urllib

from . import BASE_GRAPH_URI, SCHEMA_GRAPH_URI, _get_postgresql_config_string

def getAncestors(g, classUriRef, ancestors):
  if not classUriRef:
    return False

  for a in g.objects(classUriRef, RDFS['subClassOf']):
    ancestors.append(str(a))
    getAncestors(g, a, ancestors)

  return

def _isSubClassOf(g, classUriRef, ancestorUriRef):
  for a in g.objects(classUriRef, RDFS['subClassOf']):
    if a == ancestorUriRef:
      return True
    else:
      if _isSubClassOf(g, a, ancestorUriRef):
        return True

  return False

def isSubClassOf(g, classUriRef, ancestorUriRef):
  if not classUriRef:
    return False
  if classUriRef == ancestorUriRef:
    return True
  else:
    return _isSubClassOf(g, classUriRef, ancestorUriRef)

class PropertiesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id):

    citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(BASE_GRAPH_URI))
    
    rt = citg.open(_get_postgresql_config_string(), create=False)
    
    assert rt == VALID_STORE,"The underlying store is corrupted"

    g = Graph(citg.store, SCHEMA_GRAPH_URI)

    classUR = URIRef(class_id)

    result = []

    def getPropertyJSON(uriRef):
      # create a list of properties
      rs = g.query(' \
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
        PREFIX owl: <http://www.w3.org/2002/07/owl#> \
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
        SELECT ?property ?label ?range ?type \
        WHERE { \
                { ?property rdfs:domain <' + str(uriRef) + '> \
                  OPTIONAL { ?property rdfs:label ?label } \
                  OPTIONAL { ?property rdfs:range ?range } \
                  OPTIONAL { ?property rdf:type ?type } \
                  FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#ObjectProperty")) \
                } \
                UNION \
                { ?property rdfs:domain <' + str(uriRef) + '> \
                  OPTIONAL { ?property rdfs:label ?label } \
                  OPTIONAL { ?property rdfs:range ?range } \
                  OPTIONAL { ?property rdf:type ?type } \
                  FILTER(STRSTARTS(STR(?type), "http://www.w3.org/2002/07/owl#DatatypeProperty")) \
                } \
              } \
        ORDER BY ?label')  
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
          getAncestors(g, prop[2], ancestors)

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
        'name': l[0][1] if len(l) > 0 else '',
        'classUri': urllib.quote(uriRef),
        'comment': g.comment(uriRef),
        'properties': properties }

    # output everything about my superclasses
    def dumpSupers(subUR):
      for superUR in g.objects(subUR, RDFS['subClassOf']): 
        result.append(getPropertyJSON(superUR))
        dumpSupers(superUR)
   
    result.append(getPropertyJSON(classUR))
    dumpSupers(classUR)
    
    citg.close()

    # reverse result
    return result[::-1]
  

  def create(self, request):
    pass


  
  
  
'''
Created on Apr 3, 2013

@author: howard
'''
from rdflib import BNode, Literal, URIRef, RDF, OWL, RDFS

from . import get_schema_and_lookup_for

RDF_type = RDF['type']
OWL_DatatypeProperty = OWL['DatatypeProperty']
OWL_ObjectProperty = OWL['ObjectProperty']
RDF_Property = RDF['Property']
RDFS_Class = RDFS['Class']


def literal_from_json(sg, ug, obj, litPredicate, predSchema):
  return Literal(obj)


def seq_from_json(sg, ug, jsonObj, seqPredicate):
  
  objType = jsonObj.get('type')
  objData = jsonObj.get('data', [])

  if objType and objType != str(RDF['Seq']):
    raise Exception("Unexpected type")

  bNodeSeq = BNode()
  ug.add((bNodeSeq, RDF['type'], RDF['Seq']))

  for idx, element in enumerate(objData):

    subject = None

    if type(element) == type({}):
      subject = object_from_json(sg, ug, element, None, None)
    elif type(element) == type([]):
      subject = seq_from_json(sg, ug, element, None, None)
    else:
      subject = literal_from_json(sg, ug, element, None, None)

    ug.add((bNodeSeq, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#_{0}'.format(idx+1)), subject))

  # - end seq elements

  return bNodeSeq

def object_from_json(sg, ug, jsonObj, objPredicate, schema):

  objData = jsonObj.get('data', {})
  objId = jsonObj.get('id')

  objNode = URIRef(objId) if objId else BNode()

  # determine type of object - get it from data predicate
  classURIStr = objData.get(str(RDF_type))
  if not classURIStr:
    raise Exception("Missing require RDF['type']")

  classURIRef = URIRef(classURIStr)

  # lookup schema if none passed
  if schema:
    # ensure that type matches schema's range
    if classURIStr != schema.get('range'):
      raise Exception("Unexpected type")

  # get the schema for the specified type
  schema, lookup = get_schema_and_lookup_for(sg, classURIRef)

  # set the object's type 
  ug.add((objNode, RDF['type'], classURIRef))

  # the data for object is an object.  process each predicate.
  # for each lookup in schema
  for pred, obj in objData.iteritems():

    print pred, ' -> ', obj

    # type is handled specially
    if pred == str(RDF_type):
      continue

    predSchema = lookup.get(pred)
    if not predSchema:
      print "Cannot find schema for {0}- skipping property".format(pred)
      print "  assume CUSTOM property, skipping for now"
      continue
    
    typeUri = str(predSchema['type'])

    subject = None

    # atomic data
    if typeUri == str(OWL_DatatypeProperty) or typeUri == str(RDF_Property):
      subject = literal_from_json(sg, ug, obj, pred, predSchema)

    # object
    elif typeUri == str(OWL_ObjectProperty) or typeUri == str(RDFS_Class):
      # generalize object creation -- objects are either BNode or URIRefs
      subject = object_from_json(sg, ug, obj, pred, None)
    
    # sequence
    elif typeUri == str(RDF['Seq']):
      subject = seq_from_json(sg, ug, obj, pred)
      
    ug.add((objNode, URIRef(pred), subject))

  return objNode

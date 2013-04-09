'''
Created on Apr 3, 2013

@author: howard
'''
from rdflib import BNode, Literal, URIRef, RDF, OWL, RDFS

from . import get_schema_and_lookup_for, get_full_schema_and_lookup_for

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

    elementNode = None

    if type(element) == type({}):
      elementNode = object_from_json(sg, ug, element, None, None)
    elif type(element) == type([]):
      elementNode = seq_from_json(sg, ug, element, None, None)
    else:
      elementNode = literal_from_json(sg, ug, element, None, None)

    ug.add((bNodeSeq, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#_{0}'.format(idx+1)), elementNode))

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
    
    else:
        raise Exception("Unsupported type: {0}".format(typeUri))

    ug.add((objNode, URIRef(pred), subject))

  return objNode


def seq_to_json(sg, ug, seqNode):

  items = ug.seq(seqNode)
  if not items:
    raise Exception("Node is not of type RDF['Seq']")

  query = """
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  SELECT ?seq_index ?seq_item ?type WHERE {{
       <{0}> ?seq_index ?seq_item .
       ?seq_item rdf:type ?type .
  }}
  """

  query = query.format(str(seqNode))

  objData = []
  for idx, node, nodeType in ug.query(query):

    print idx, node, nodeType

    seqItem = None
    if type(node) == Literal:
      seqItem = str(node)
    elif type(node) == URIRef:
      seqItem = str(node)
    elif type(node) == BNode:
      # must have an RDF['type']
      objType = list(ug.objects(node, RDF['type']))[0]
      if objType == RDF['Seq']:
        seqItem = seq_to_json(sg, ug, node)
      else:
        seqItem = object_to_json(sg, ug, node)
    else:
      raise Exception("Unsupported type: {0]".format(type(node)))

    objData.append(seqItem)

  return objData

def object_to_json(sg, ug, objectNode):
  
  query = ' \
    SELECT ?predicate ?object \
    WHERE {{ \
      <{0}> ?predicate ?object \
    }}'.format(str(objectNode))

  propDict = {}
  for pred, obj in ug.query(query):
    propDict[str(pred)] = obj

  # get the type so we can get the schema
  classURIStr = propDict.get(str(RDF['type']))

  if not classURIStr:
    raise Exception('Missing require RDF[\'type\']')

  # get the schema for the specified type
  schema, lookup = get_full_schema_and_lookup_for(sg, URIRef(classURIStr))

  objData = {}
  for pred, obj in propDict.iteritems():
    if type(obj) == Literal:
      objData[pred] = str(obj)
    elif type(obj) == URIRef:
      objData[pred] = str(obj)
    elif type(obj) == BNode:
      predSchema = lookup.get(pred)
      typeUri = str(predSchema['type'])

      # object
      if typeUri == str(OWL_ObjectProperty) or typeUri == str(RDFS_Class):
        # generalize object creation -- objects are either BNode or URIRefs
        objData[pred] = object_to_json(sg, ug, obj)
      
      # sequence
      elif typeUri == str(RDF['Seq']):
        objData[pred] = seq_to_json(sg, ug, obj)

      else:
        raise Exception("Unsupported type: {0}".format(typeUri))

  return {'data': objData, 'schema': schema }

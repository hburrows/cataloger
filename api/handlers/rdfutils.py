'''
Created on Apr 3, 2013

@author: howard
'''
import numbers
from datetime import datetime
import calendar

import dateutil.parser

from rdflib import BNode, Literal, URIRef, RDF, OWL, RDFS, Namespace

import rdflib_sparql
rdflib_sparql.SPARQL_LOAD_GRAPHS = False

from api import COMMON_GRAPH_URI
from . import sparql_query, sparql_update, get_schema_and_lookup_for, get_full_schema_and_lookup_for

COMMON = Namespace(COMMON_GRAPH_URI)

RDF_type = RDF['type']
RDF_Seq = RDF['Seq']
OWL_DatatypeProperty = OWL['DatatypeProperty']
OWL_ObjectProperty = OWL['ObjectProperty']
RDF_Property = RDF['Property']
RDFS_Class = RDFS['Class']


def seq_to_json(graphs, cg_uri, ug_uri, subject_uri, predicates=None, schema=None):

  predicates = predicates if predicates else []

  selector = '{selector}'
  for predicate in predicates:
    selector = selector.format(selector=' <' + predicate + '> [ {selector} ] ')
  selector = selector.format(selector='?predicate ?object')

  rq_tmpl = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
PREFIX : <{ug_uri}>
SELECT ?predicate ?object ?type
WHERE {{
  GRAPH : {{
    <{subject_uri}> {selector} .
    OPTIONAL {{ ?object rdf:type ?type . }}
  }}
}}'''

  rq = rq_tmpl.format(ug_uri=ug_uri, subject_uri=subject_uri, selector=selector)

  objData = []
  for result in sparql_query(rq)["results"]["bindings"]:

    predicate = result['predicate']['value']

    # skip the rdf:type predicate -- but make sure it's an rdf:Seq first
    if predicate == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
      if result['object']['value'] != 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq':
        raise Exception('Invalid type -- expected type to be sequence')
      continue

    obj_data_type = result['object']['type']
    obj_json = None
    if obj_data_type == 'literal':
      obj_json = Literal(result['object']['value'])
    elif obj_data_type == 'uri':
      
      object_uri = URIRef(result['object']['value'])

      # embed the object depending on schema definition
      if schema.get('embed', False):
      
        object_rdf_type = result['type']['value']

        if object_rdf_type == RDF['Seq']:
          obj_json = seq_to_json(graphs, cg_uri, ug_uri, object_uri)
        else:
          obj_json = object_to_json(graphs, cg_uri, ug_uri, object_uri)

      else:
        obj_json = {'id': object_uri}

    elif obj_data_type == 'bnode':
      
      bnode_type = result['type']['value']

      predicates.append(predicate)

      if bnode_type == RDF['Seq']:
        obj_json = seq_to_json(graphs, cg_uri, ug_uri, subject_uri, predicates)
      else:
        obj_json = object_to_json(graphs, cg_uri, ug_uri, subject_uri, predicates)

      predicates.pop()

    else:
      raise Exception("Unsupported type: {0]".format(obj_data_type))

    objData.append(obj_json)

  return objData



def object_to_json(graphs, cg_uri, ug_uri, entry_uri, predicates=None):

  predicates = predicates if predicates else []

  selector = '{selector}'
  for predicate in predicates:
    selector = selector.format(selector=' <' + predicate + '> [ {selector} ] ')
  selector = selector.format(selector='?predicate ?object')

  rq_tmpl = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <{ug_uri}>
SELECT ?predicate ?object
WHERE {{
  GRAPH : {{
    <{subject_uri}> {selector}
  }}
}}'''

  rq = rq_tmpl.format(ug_uri=ug_uri, subject_uri=entry_uri, selector=selector)

  propDict = {}
  for result in sparql_query(rq)["results"]["bindings"]:
    obj_data_type = result['object']['type']
    if obj_data_type == 'literal':
      propDict[result['predicate']['value']] = Literal(result['object']['value'])
    elif obj_data_type == 'typed-literal':

      datatype = result['object']['datatype']
      literal = None
      
      if datatype == 'http://www.w3.org/2001/XMLSchema#dateTime':
        datetime = dateutil.parser.parse(result['object']['value'])
        literal = calendar.timegm(datetime.timetuple())
      elif datatype == 'http://www.w3.org/2001/XMLSchema#integer':
        literal = int(result['object']['value'])
      else:
        literal = result['object']['value']
      propDict[result['predicate']['value']] = Literal(literal)
    elif obj_data_type == 'uri':
      propDict[result['predicate']['value']] = URIRef(result['object']['value'])
    elif obj_data_type == 'bnode':
      propDict[result['predicate']['value']] = BNode(result['object']['value'])
    else:
      raise Exception("Unrecognized type: {0}".format(obj_data_type))


  # get the type so we can get the schema
  type_uri = propDict.get(str(RDF['type']))

  if not type_uri:
    raise Exception('Missing require RDF[\'type\']')

  # get the schema for the specified type
  schema, lookup = get_full_schema_and_lookup_for(graphs, type_uri)

  objData = {}
  for pred, obj in propDict.iteritems():
    
    if type(obj) == Literal:
      objData[pred] = str(obj)
    elif type(obj) == URIRef:
      objData[pred] = str(obj)
    elif type(obj) == BNode:
      predSchema = lookup.get(pred)
      typeUri = str(predSchema['type'])

      predicates.append(pred)

      # object
      if typeUri == str(OWL_ObjectProperty) or typeUri == str(RDFS_Class):
        # generalize object creation -- objects are either BNode or URIRefs
        objData[pred] = object_to_json(graphs, cg_uri, ug_uri, entry_uri, predicates)
      
      # sequence
      elif typeUri == str(RDF['Seq']):
        objData[pred] = seq_to_json(graphs, cg_uri, ug_uri, entry_uri, predicates, predSchema)

      else:
        raise Exception("Unsupported type: {0}".format(typeUri))

      predicates.pop()

  # package into standard JSON
  result = {'data': objData, 'schema': schema }

  if entry_uri and len(predicates) == 0:
    result['id'] = entry_uri
    
  return result

'''
  #################################################################

    UPDATE functionality

  #################################################################

'''

def _delete_triple(ug_uri, subject, predicate, obj):
  # delete the triple and any recursively attached
  # to object of triple
  # ??? TODO recursively delete

  # atomic data
  if type(obj) == Literal:
    ug_uri.remove((subject, predicate, obj))

  # object
  elif type(obj) == URIRef:
    ug_uri.remove((subject, predicate, obj))
    
  elif type(obj) == BNode:
    # recursively delete each triple this object is the subject of
    for t in ug_uri.triples((obj, None, None)):
      _delete_triple(ug_uri, obj, t[1], t[2])

  else:
    raise Exception("Unsupported type: {0}".type(obj))



def _insert_triple_frag(graphs, predicate, obj_json, pred_metadata):

  frag = None

  pred_type = str(pred_metadata['type']) if pred_metadata else None

  # switch on how to interpret the data

  # special case for rdf['type']
  if predicate == str(RDF_type):
    frag = '<{0}> <{1}>'.format(predicate, obj_json)
    
  # literal data
  elif pred_type == str(OWL_DatatypeProperty) or pred_type == str(RDF_Property):
    # s p o .
    if isinstance(obj_json, basestring):
      frag = '<{0}> "{1}"'.format(predicate, obj_json)
    elif isinstance(obj_json, numbers.Number):
      frag = '<{0}> {1}'.format(predicate, obj_json)
    else:
      raise Exception("unexpected json type for Literal")
  
  # object
  elif pred_type == str(OWL_ObjectProperty):
    # generalize object creation -- objects are either BNode or URIRefs
    if type(obj_json) == dict:
      # bnode
      # [ ... ] .

      frag = _insert_object_frag(graphs, predicate, obj_json)
        
    elif isinstance(obj_json, basestring):
      # uriref
      # s p o .
      frag = '<{0}> <{1}>'.format(predicate, obj_json)

    elif not pred_type:
      print "No metadata for {0}- skipping property".format(predicate)
      print "NOT IMPLEMENTED: CUSTOM property, skipping for now"
      
    else:
      # error
      raise Exception("Unxpected")
    
  # sequence
  elif pred_type == str(RDF['Seq']):
    # Seq
    # NOTE: currently only support bnodes as array elements
    # [ a rdf:Seq ; rdf:_1 [] ; rdf:_2 [] ]
      # predicate/object data
    el_data = obj_json.get('data', [])
    
    if type(el_data) != list:
      raise Exception("unexpected json type for Seq")
    
    po_frags = []
    po_frags.append('<{0}> <{1}>'.format(str(RDF_type), 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq'))

    for idx, el_json in enumerate(el_data):

      el_predicate = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_{0}'.format(idx+1)
      
      frag = _insert_object_frag(graphs, el_predicate, el_json)

      po_frags.append(frag)
      
    frag = '<{0}> [ {1} ]'.format(predicate, ' ; '.join(po_frags))
  
  elif pred_type == None:
    print "No metadata for {0}".format(predicate)
    print "Will store as untyped sub, pred, obj"
    frag = '<{0}> "{1}"'.format(predicate, obj_json)
     
  else:
      raise Exception("Unsupported type: {0}".format(predicate))

  return frag


def _insert_object_frag(graphs, predicate, obj_json):

  if 'id' in obj_json:
    # ??? NO check if object actually represents required range.  Perform
    #     lookup and ensure compatibility
    return '<{0}> <{1}>'.format(predicate, obj_json['id'])

  # predicate/object data
  po_data = obj_json.get('data', {})
  
  # determine class of object
  type_uri = po_data.get(str(RDF_type))
  if not type_uri:
    raise Exception("Missing require RDF['type']")
  
  # describe the type
  schema, lookup = get_schema_and_lookup_for(graphs, type_uri)
  
  # for each item in data determine if new or exists and INSERT OR UPDATE as appropriate
  #
  po_frags = []
  for prop_p, prop_o in po_data.iteritems():

    pred_metadata = lookup.get(prop_p)
#     if not pred_metadata:
#       print "Cannot find metadata for {0}- skipping property".format(prop_p)
#       print "  assume CUSTOM property, skipping for now"
#       continue
    
    po_frags.append(_insert_triple_frag(graphs, prop_p, prop_o, pred_metadata))
    
  frag = '<{0}> [ {1} ]'.format(predicate, ' ; '.join(po_frags))
  
  return frag

'''

'''  
def _update_triple_frag(sg_uri, ug_uri, subject, predicate, new_json, existing_obj, pred_metadata):

  obj_update = None

  # determine update if any based on predicate type
  pred_type = str(pred_metadata['type']) if pred_metadata else None

  # based on the type determine if the object has changed

  if predicate == str(RDF_type):
    if new_json != existing_obj:
      print("rdf:type update")
      obj_update = '<' + new_json + '>'

  # literal data
  elif pred_type == str(OWL_DatatypeProperty) or pred_type == str(RDF_Property):
    # s p o .
    if isinstance(new_json, basestring):
      if new_json != existing_obj:
        print(predicate + "; literal:string update")
        obj_update = '"' + new_json + '"'
    elif isinstance(new_json, numbers.Number):
      if str(new_json) != existing_obj:
        print(predicate + '; literal:int update')
    else:
      raise Exception("unexpected json type for Literal")
  
  # object data
  elif pred_type == str(OWL_ObjectProperty):

    if type(new_json) == dict:
      # bnode
      pass
        
    elif isinstance(new_json, basestring):
      # uriref
      if new_json != existing_obj:
        print(predicate + "; uri update")
        obj_update = '<' + new_json + '>'

  # sequence
  elif pred_type == str(RDF['Seq']):
    pass

  elif not pred_type:
    print "No metadata for {0}".format(predicate)
    print "Will store as untyped sub, pred, obj"
    if new_json != existing_obj:
      print(predicate + "; unknown type update")
      
  else:
    # it's some type of predicate that we're not prepared to handle
    raise Exception("Unexpected predicate type for update: " + pred_type)

  frag = None
  
  if obj_update:
    frag = 'WITH : DELETE {{ <{subject}> <{predicate}> ?o }} INSERT {{ <{subject}> <{predicate}> {update} }} WHERE {{ <{subject}> <{predicate}> ?o }}'.format(subject=subject, predicate=predicate, update=obj_update)

  return frag

def _update_object_frag(sg_uri, ug_uri, predicate, new_json, existing_json):
  frag = None
  return frag


'''
   MAIN update driver
'''
def update_from_json(graphs, ug_uri, sg_uri, subject, jsonObj):

  # predicate/object data
  po_data = jsonObj.get('data', {})

  # remove createTime and updateTime from input data as these are
  # handle specially
  po_data.pop(str(COMMON['createTime']), None)
  po_data.pop(str(COMMON['updateTime']), None)
  
  # determine class of subject
  type_str = po_data.get(str(RDF_type))
  if not type_str:
    raise Exception("Missing require RDF['type']")

  # query the graph for subject's existing predicates/objects.
  template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <{ug_uri}>
SELECT ?p ?o
FROM NAMED <{ug_uri}>
WHERE {{
  GRAPH : {{
    <{subject}> ?p ?o .
  }}
}}
'''
  rq = template.format(subject=subject, ug_uri=ug_uri)

  # copy resultset into dictionary to track which are new,
  # updated, and deleted
  existingProps = {}  
  for result in sparql_query(rq)["results"]["bindings"]:
    p = result['p']['value']
    o = result['o']['value']    
    existingProps[p] = o

  insert_frags = []
  update_frags = []

  # handle the insert/update for createTime and updateTime properties specially
  if str(COMMON['createTime']) not in existingProps:
    insert_frags.append('<{0}> {1} "{2}"^^xsd:dateTime'.format(subject, "common:createTime", datetime.now().isoformat()))
  else:
    del existingProps[str(COMMON['createTime'])]
    
  if str(COMMON['updateTime']) in existingProps:
    update_frags.append('WITH : DELETE {{ <{subject}> common:updateTime ?o }} INSERT {{ <{subject}> common:updateTime "{time}"^^xsd:dateTime }} WHERE {{ <{subject}> common:updateTime ?o }}'.format(subject=subject, time=datetime.now().isoformat()))
    del existingProps[str(COMMON['updateTime'])]
  else:
    insert_frags.append('<{0}> {1} "{2}"^^xsd:dateTime'.format(subject, "common:updateTime", datetime.now().isoformat()))

  # get the schema for the specified type so we have property meta-data available
  # as a guide to assist in interpreting objects
  schema, lookup = get_schema_and_lookup_for(graphs, type_str)

  # for each item in data determine if new or existing and INSERT OR UPDATE as appropriate
  #
  for predicate, obj_json in po_data.iteritems():

    pred_metadata = lookup.get(predicate)
    
    existing_obj = existingProps.get(predicate)

    if existing_obj:
      # update
      frag = _update_triple_frag(sg_uri, ug_uri, subject, predicate, obj_json, existing_obj, pred_metadata)
      if frag:
        update_frags.append(frag)

      del existingProps[predicate]

    else:
      # insert      
      insert_frags.append('<{0}> {1}'.format(subject, _insert_triple_frag(graphs, predicate, obj_json, pred_metadata)))

  # INSERTS to graph
  #
  if len(insert_frags) > 0:
    # create and execute INSERT request
    triple_inserts = ' . '.join(insert_frags)
  
    ru_tmpl = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <{ug_uri}>
PREFIX common: <{cg_uri}>
INSERT DATA {{
  GRAPH : {{
    {updates}
 }}
}} ;
'''
    ru = ru_tmpl.format(cg_uri=COMMON_GRAPH_URI, ug_uri=ug_uri, updates=triple_inserts)
  
    sparql_update(ru)

  # UPDATES to graph
  #
  if len(update_frags) > 0:
    # create and execute UPDATE request
    triple_updates = ' ; '.join(update_frags)

    ru_tmpl = '''
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <{ug_uri}>
PREFIX common: <{cg_uri}>
{updates}
'''
    ru = ru_tmpl.format(cg_uri=COMMON_GRAPH_URI, ug_uri=ug_uri, updates=triple_updates)

    sparql_update(ru)

  # DELETE any remaining existingProps
  #
  delete_frags = []
  for predicate, obj in existingProps.iteritems():
    _delete_triple(ug_uri, subject, predicate, obj)

  return
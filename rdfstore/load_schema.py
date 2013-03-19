'''
Created on Mar 6, 2013

@author: howard
'''

from rdflib import Namespace, Literal, URIRef, Graph, ConjunctiveGraph
from rdflib.store import VALID_STORE

from rdflib import RDF, RDFS, OWL, XSD

from globals import DEFAULT_GRAPH_URI, SCHEMA_GRAPH_URI

from globals import _get_postgresql_config_string


citg = ConjunctiveGraph('PostgreSQL', identifier=URIRef(DEFAULT_GRAPH_URI))
rt = citg.open(_get_postgresql_config_string(), create=False)

#from globals import _get_mysql_config_string
#citg = ConjunctiveGraph('MySQL', identifier=URIRef(DEFAULT_GRAPH_URI))
#rt = citg.open(_get_mysql_config_string(), create=False)

assert rt == VALID_STORE,"The underlying store is corrupted"



sg = Graph(citg.store, identifier=URIRef(SCHEMA_GRAPH_URI))




# owl
sg.parse('http://www.w3.org/2002/07/owl')

# RDFS and RDF vocabularies
sg.parse('http://www.w3.org/2000/01/rdf-schema#')
sg.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# DC vocabularies
sg.parse('http://purl.org/dc/elements/1.1/')
sg.parse('http://purl.org/dc/terms/')

# FOAF
sg.parse('http://xmlns.com/foaf/spec/20100809.rdf')

# review vocabulary
sg.parse('http://vocab.org/review/terms.rdf')

# declare namespaces
dcElementNS = Namespace('http://purl.org/dc/elements/1.1/')
dcTermNS = Namespace('http://purl.org/dc/terms/')

foafNS = Namespace('http://xmlns.com/foaf/0.1/')

schemaNS = Namespace(SCHEMA_GRAPH_URI)

sg.bind('owl', OWL)
sg.bind('cits', schemaNS)

owlClass = OWL['Class']
owlObjectProperty = OWL['ObjectProperty']
owlDatatypeProperty = OWL['DatatypeProperty']

rdfType = RDF['type']

rdfsSubClassOf = RDFS['subClassOf']
rdfsDomain = RDFS['domain']
rdfsRange = RDFS['range']
rdfsLabel = RDFS['label']
isDefinedBy = RDFS['isDefinedBy']

xsdString = XSD['string']

dcTitle = dcElementNS['title']
dcDescription = dcElementNS['description']
dcCreator = dcElementNS['creator']
dcDateSubmitted = dcElementNS['dateSubmitted']

foafAgent = foafNS['Agent']

collectableClass = schemaNS['Collectable']
basketClass = schemaNS['Basket']
rugClass = schemaNS['Rug']
maskClass = schemaNS['Mask']
dollClass = schemaNS['Doll']
carvedStoneClass = schemaNS['CarvedStone']
pipeClass = schemaNS['Pipe']

valuationClass = schemaNS['Valuation']

# define properties
isUsedFor = schemaNS['isUsedFor']

aquirePrice = schemaNS['aquireDate']
aquireDate = schemaNS['aquirePrice']
valuation = schemaNS['valuationOn']
tags = schemaNS['tags']
valuationValue = schemaNS['valuation.value']
valuationDate = schemaNS['valuation.date']
valuationAgent = schemaNS['valuation.agent']

catalogitLiteral = Literal('catalogit')

usedForPrimary = Literal('primary')
usedForSecondary = Literal('secondary')

collectableSchema = [

  # class declarations
  (collectableClass, rdfType, owlClass),
  #(collectableClass, rdfsSubClassOf, OWL['Thing']),
  (collectableClass, rdfsLabel, Literal('Collectable')),
  (collectableClass, isDefinedBy, catalogitLiteral),
  (collectableClass, isUsedFor, usedForPrimary),

  (basketClass, rdfType, owlClass),
  (basketClass, rdfsLabel, Literal('Basket')),
  (basketClass, rdfsSubClassOf, collectableClass),
  (basketClass, isDefinedBy, catalogitLiteral),
  (basketClass, isUsedFor, usedForPrimary),

  (rugClass, rdfType, owlClass),
  (rugClass, rdfsSubClassOf, collectableClass),
  (rugClass, rdfsLabel, Literal('Rug')),
  (rugClass, isDefinedBy, catalogitLiteral),
  (rugClass, isUsedFor, usedForPrimary),

  (maskClass, rdfType, owlClass),
  (maskClass, rdfsSubClassOf, collectableClass),
  (maskClass, rdfsLabel, Literal('Mask')),
  (maskClass, isDefinedBy, catalogitLiteral),
  (maskClass, isUsedFor, usedForPrimary),

  (dollClass, rdfType, owlClass),
  (dollClass, rdfsSubClassOf, collectableClass),
  (dollClass, rdfsLabel, Literal('Doll')),
  (dollClass, isDefinedBy, catalogitLiteral),
  (dollClass, isUsedFor, usedForPrimary),

  (carvedStoneClass, rdfType, owlClass),
  (carvedStoneClass, rdfsSubClassOf, collectableClass),
  (carvedStoneClass, rdfsLabel, Literal('Carved Stone')),
  (carvedStoneClass, isDefinedBy, catalogitLiteral),
  (carvedStoneClass, isUsedFor, usedForPrimary),

  (pipeClass, rdfType, owlClass),
  (pipeClass, rdfsSubClassOf, collectableClass),
  (pipeClass, rdfsLabel, Literal('Pipe')),
  (pipeClass, isDefinedBy, catalogitLiteral),
  (pipeClass, isUsedFor, usedForPrimary),
  
  (valuationClass, rdfType, owlClass),
  (valuationClass, rdfsLabel, Literal('Valuation')),
  (valuationClass, isUsedFor, usedForSecondary),

  (isUsedFor, rdfType, owlDatatypeProperty),
  (isUsedFor, rdfsLabel, Literal('A tag used to indicate how a class is used.')),
  (isUsedFor, rdfsDomain, owlClass),

  # properties of collectable
  (dcTitle, rdfsDomain, collectableClass),
  (dcDescription, rdfsDomain, collectableClass),

  (aquirePrice, rdfType, owlDatatypeProperty),
  (aquirePrice, rdfsDomain, collectableClass),
  (aquirePrice, rdfsRange, xsdString),
  (aquirePrice, rdfsLabel, Literal('Acquire Price')),
  (aquirePrice, RDFS['comment'], Literal('Cost to acquire the item.')),

  (aquireDate, rdfType, owlDatatypeProperty),
  (aquireDate, rdfsDomain, collectableClass),
  (aquireDate, rdfsRange, XSD['date']),
  (aquireDate, rdfsLabel, Literal('Acquire Date')),
  (aquireDate, RDFS['comment'], Literal('Date the item was acquired.')),

  (tags, rdfType, owlDatatypeProperty),
  (tags, rdfsDomain, collectableClass),
  (tags, rdfsRange, xsdString),
  (tags, rdfsLabel, Literal('Tags')),
  (tags, RDFS['comment'], Literal('Keywords that identify, classify, characterize the item.')),

  (valuation, rdfType, owlObjectProperty),
  (valuation, rdfsDomain, collectableClass),
  (valuation, rdfsRange, valuationClass),
  (valuation, rdfsLabel, Literal('Valuation')),
  (valuation, RDFS['comment'], Literal('Value of the item on a certain date.')),

  (valuationValue, rdfType, owlDatatypeProperty),
  (valuationValue, rdfsDomain, valuation),
  (valuationValue, rdfsRange, xsdString),
  (valuationValue, rdfsLabel, Literal('Value')),
  (valuationValue, RDFS['comment'], Literal('Real or estimated value of item.')),
  
  (valuationDate, rdfType, owlDatatypeProperty),
  (valuationDate, rdfsDomain, valuation),
  (valuationDate, rdfsRange, XSD['date']),
  (valuationDate, rdfsLabel, Literal('Date')),
  (valuationDate, RDFS['comment'], Literal('Date valuation was provided.')),

  (valuationAgent, rdfType, owlObjectProperty),
  (valuationAgent, rdfsDomain, valuation),
  (valuationAgent, rdfsRange, foafAgent),
  (valuationAgent, rdfsLabel, Literal('Provider')),
  (valuationAgent, RDFS['comment'], Literal('Person or organization that provided the valuation.')),

  (URIRef('http://xmlns.com/foaf/0.1/Image'), isUsedFor, usedForSecondary),
  (URIRef('http://xmlns.com/foaf/0.1/Agent'), isUsedFor, usedForSecondary),

  (URIRef('http://xmlns.com/foaf/0.1/Person'), isUsedFor, usedForPrimary),
  (URIRef('http://purl.org/dc/terms/Location'), isUsedFor, usedForSecondary),
  (URIRef('http://purl.org/dc/terms/BibliographicResource'), isUsedFor, usedForSecondary),
  (URIRef('http://xmlns.com/foaf/0.1/Organization'), isUsedFor, usedForSecondary),
  
  (URIRef('http%3A//purl.org/dc/terms/Agent'), isUsedFor, usedForSecondary),
  (URIRef('http%3A//www.w3.org/2000/10/swap/pim/contact%23Person'), isUsedFor, usedForSecondary)
]

for t in collectableSchema: sg.add(t)

#lifeLoggerNS = Namespace(DEFAULT_GRAPH_URI + '_lifelogger/')
#
#eventClass = lifeLoggerNS['Activity']
#
#sleptClass = lifeLoggerNS['Slept']
#ateClass = lifeLoggerNS['Ate']
#drankClass = lifeLoggerNS['Drank']
#sweatClass = lifeLoggerNS['Sweat']
#playedClass = lifeLoggerNS['Played']
#workedClass = lifeLoggerNS['Worked']
#watchedClass = lifeLoggerNS['Watched']
#feltClass = lifeLoggerNS['Felt']

sg.commit()

citg.close()

print "Successfully loaded schema."
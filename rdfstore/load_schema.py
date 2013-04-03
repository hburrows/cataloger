'''
Created on Mar 6, 2013

@author: howard
'''

from rdflib import Namespace, Literal, URIRef, Graph, ConjunctiveGraph, plugin
from rdflib.store import Store, VALID_STORE

from rdflib import RDF, RDFS, OWL, XSD

from api import BASE_GRAPH_URI, SCHEMA_GRAPH_URI, DATABASE_STORE, _get_db_config_string


store = plugin.get(DATABASE_STORE, Store)(identifier='rdfstore')

rt = store.open(_get_db_config_string(), create=False)
assert rt == VALID_STORE,"The underlying store is corrupted"
        
citg = ConjunctiveGraph(store, identifier=URIRef(BASE_GRAPH_URI))

sg = Graph(store, identifier=URIRef(SCHEMA_GRAPH_URI))



# owl
sg.parse('http://www.w3.org/2002/07/owl')

# RDFS and RDF vocabularies
sg.parse('http://www.w3.org/2000/01/rdf-schema#')
sg.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

# DC vocabularies
sg.parse('http://purl.org/dc/elements/1.1/')
sg.parse('http://purl.org/dc/terms/')
sg.parse('http://purl.org/dc/dcmitype/')

# FOAF
sg.parse('http://xmlns.com/foaf/0.1/')

# GEO - i.e. latitude and longitude
sg.parse('http://www.w3.org/2003/01/geo/wgs84_pos#')


sg.commit()


# declare namespaces
DC = Namespace('http://purl.org/dc/elements/1.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
DCMI = Namespace('http://purl.org/dc/dcmitype/')

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

GEO = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

schemaNS = Namespace(SCHEMA_GRAPH_URI)

sg.bind('owl', OWL)
sg.bind('cits', schemaNS)

owlClass = OWL['Class']
owlObjectProperty = OWL['ObjectProperty']
owlDatatypeProperty = OWL['DatatypeProperty']

rdfType = RDF['type']
rdfBag = RDF['Bag']
rdfSeq = RDF['Seq']
rdfAlt = RDF['Alt']

rdfsSubClassOf = RDFS['subClassOf']
rdfsDomain = RDFS['domain']
rdfsRange = RDFS['range']
rdfsLabel = RDFS['label']
isDefinedBy = RDFS['isDefinedBy']

xsdString = XSD['string']

dcTitle = DC['title']
dcDescription = DC['description']
dcCreator = DC['creator']
dcDateSubmitted = DC['dateSubmitted']

dcImage = DCMI['Image']

dcMovingImage = DCMI['MovingImage']

dcStillImage = DCMI['StillImage']
stillImageType = schemaNS['stillImageType']
stillImageURL = schemaNS['stillImageURL']
stillImageWidth = schemaNS['stillImageWidth']
stillImageHeight = schemaNS['stillImageHeight']

dcSound = DCMI['Sound']

dcText = DCMI['Text']

cdInteractiveResource = DCMI['InteractiveResource']

foafAgent = FOAF['Agent']

EntryClass = schemaNS['Entry']
CollectableClass = schemaNS['Collectable']
basketClass = schemaNS['Basket']
rugClass = schemaNS['Rug']
maskClass = schemaNS['Mask']
dollClass = schemaNS['Doll']
carvedStoneClass = schemaNS['CarvedStone']
pipeClass = schemaNS['Pipe']

valuationClass = schemaNS['Valuation']

# define properties
isUsedFor = schemaNS['isUsedFor']
usedForPrimary = Literal('primary')
usedForSecondary = Literal('secondary')

media = schemaNS['media']
createTime = schemaNS['createTime']
updateTime = schemaNS['updateTime']

aquirePrice = schemaNS['aquireDate']
aquireDate = schemaNS['aquirePrice']
valuation = schemaNS['valuationOn']
tags = schemaNS['tags']
tagContainer = schemaNS['tagContainer']
valuationValue = schemaNS['valuation.value']
valuationDate = schemaNS['valuation.date']
valuationAgent = schemaNS['valuation.agent']

catalogitLiteral = Literal('catalogit')

displayOrder = schemaNS['displayOrder']
userEditable = schemaNS['userEditable']


'''
# utility class declarations
#
(stillImageSeq, rdfType, owlClass),
(stillImageSeq, rdfsSubClassOf, RDF['Seq']),
(stillImageSeq, rdfsLabel, Literal('Still Images')),
(stillImageSeq, RDFS['comment'], Literal('A collection of still images of or related to the item.')),  
(stillImageSeq, isDefinedBy, catalogitLiteral),
(stillImageSeq, isUsedFor, usedForSecondary),

(schemaNS['TagContainer'], rdfType, owlClass),
(schemaNS['TagContainer'], rdfsSubClassOf, RDF['Seq']),
(schemaNS['TagContainer'], rdfsLabel, Literal('Tag Container')),
(schemaNS['TagContainer'], RDFS['comment'], Literal('A container of arbitrary xsd:string literals intended to be used for keywords of a user\'s choosing that identify, classify, and/or characterize items.')),  
(schemaNS['TagContainer'], isDefinedBy, catalogitLiteral),
(schemaNS['TagContainer'], isUsedFor, usedForSecondary),


(schemaNS['MediaContainer'], rdfType, owlClass),
(schemaNS['MediaContainer'], rdfsSubClassOf, RDF['Seq']),
(schemaNS['MediaContainer'], rdfsLabel, Literal('Media Container')),
(schemaNS['MediaContainer'], RDFS['comment'], Literal('A container for storing different types of media associated with an item.')),  
(schemaNS['MediaContainer'], isDefinedBy, catalogitLiteral),
(schemaNS['MediaContainer'], isUsedFor, usedForSecondary),
'''

collectableSchema = [

  # utility class declarations
  #
  (schemaNS['StillImage'], rdfType, owlClass),
  (schemaNS['StillImage'], rdfsLabel, Literal('Still Image')),
  (schemaNS['StillImage'], isUsedFor, usedForSecondary),

  (schemaNS['location'], rdfType, owlObjectProperty),
  (schemaNS['location'], rdfsDomain, schemaNS['StillImage']),
  (schemaNS['location'], rdfsRange, GEO['Point']),
  (schemaNS['location'], rdfsLabel, Literal('Location')),
  
  (schemaNS['images'], rdfType, RDF['Seq']),
  (schemaNS['images'], rdfsDomain, schemaNS['StillImage']),

  (stillImageType, rdfType, owlDatatypeProperty),
  (stillImageType, rdfsDomain, dcStillImage),
  (stillImageType, rdfsRange, XSD['string']),
  
  (stillImageURL, rdfType, owlDatatypeProperty),
  (stillImageURL, rdfsDomain, dcStillImage),
  (stillImageURL, rdfsRange, XSD['string']),
  
  (stillImageWidth, rdfType, owlDatatypeProperty),
  (stillImageWidth, rdfsDomain, dcStillImage),
  (stillImageWidth, rdfsRange, XSD['integer']),
  
  (stillImageHeight, rdfType, owlDatatypeProperty),
  (stillImageHeight, rdfsDomain, dcStillImage),
  (stillImageHeight, rdfsRange, XSD['integer']),
  
  (displayOrder, rdfType, owlDatatypeProperty),
  (displayOrder, rdfsDomain, owlDatatypeProperty),
  (displayOrder, rdfsRange, XSD['integer']),
  
  # cit class declarations
  #
  (EntryClass, rdfType, owlClass),
  #(EntryClass, rdfsSubClassOf, OWL['Thing']),  
  (EntryClass, rdfsLabel, Literal('Entry')),
  (EntryClass, isDefinedBy, catalogitLiteral),

  (createTime, rdfType, owlDatatypeProperty),
  (createTime, displayOrder, Literal('1')),
  (createTime, rdfsDomain, EntryClass),
  (createTime, rdfsRange, XSD['dateTime']),
  (createTime, rdfsLabel, Literal('Create Time')),
  (createTime, RDFS['comment'], Literal('Date and time entry was entered into catalog.')),

  (updateTime, rdfType, owlDatatypeProperty),
  (updateTime, displayOrder, Literal('2')),
  (updateTime, rdfsDomain, EntryClass),
  (updateTime, rdfsRange, XSD['dateTime']),
  (updateTime, rdfsLabel, Literal('Update Time')),
  (updateTime, RDFS['comment'], Literal('Date and time entry was last updated.')),

  (media, rdfType, RDF['Seq']),
  (media, displayOrder, Literal('3')),
  (media, rdfsDomain, EntryClass),
  (media, rdfsRange, schemaNS['StillImage']),
  (media, rdfsLabel, Literal('Media Container')),
  (media, RDFS['comment'], Literal('The set of media (images, videos, sounds, documents, etc.) associated with the item.')),

  (isUsedFor, rdfType, owlDatatypeProperty),
  (isUsedFor, rdfsDomain, EntryClass),
  (isUsedFor, rdfsLabel, Literal('A tag used to indicate how a class is used.')),

  (valuationClass, rdfType, owlClass),
  (valuationClass, rdfsLabel, Literal('Valuation')),
  (valuationClass, isUsedFor, usedForSecondary),

  (valuationValue, rdfType, owlDatatypeProperty),
  (valuationValue, displayOrder, Literal('1')),
  (valuationValue, rdfsDomain, valuation),
  (valuationValue, rdfsRange, XSD['decimal']),
  (valuationValue, rdfsLabel, Literal('Value')),
  (valuationValue, RDFS['comment'], Literal('Real or estimated value of item.')),
  
  (valuationDate, rdfType, owlDatatypeProperty),
  (valuationDate, displayOrder, Literal('2')),
  (valuationDate, rdfsDomain, valuation),
  (valuationDate, rdfsRange, XSD['date']),
  (valuationDate, rdfsLabel, Literal('Date')),
  (valuationDate, RDFS['comment'], Literal('Date valuation was provided.')),

  (valuationAgent, rdfType, owlObjectProperty),
  (valuationAgent, displayOrder, Literal('3')),
  (valuationAgent, rdfsDomain, valuation),
  (valuationAgent, rdfsRange, foafAgent),
  (valuationAgent, rdfsLabel, Literal('Provider')),
  (valuationAgent, RDFS['comment'], Literal('Person or organization that provided the valuation.')),

  (CollectableClass, rdfType, owlClass),
  (CollectableClass, rdfsSubClassOf, EntryClass),
  (CollectableClass, rdfsLabel, Literal('Collectable')),
  (CollectableClass, isDefinedBy, catalogitLiteral),
  (CollectableClass, isUsedFor, usedForPrimary),

  # properties of collectable
  (dcTitle, rdfsDomain, CollectableClass),
  (dcTitle, displayOrder, Literal('1')),

  (dcDescription, rdfsDomain, CollectableClass),
  (dcDescription, displayOrder, Literal('2')),

  (aquireDate, rdfType, owlDatatypeProperty),
  (aquireDate, displayOrder, Literal('3')),
  (aquireDate, rdfsDomain, CollectableClass),
  (aquireDate, rdfsRange, XSD['date']),
  (aquireDate, rdfsLabel, Literal('Acquire Date')),
  (aquireDate, RDFS['comment'], Literal('Date the item was acquired.')),

  (aquirePrice, rdfType, owlDatatypeProperty),
  (aquirePrice, displayOrder, Literal('4')),
  (aquirePrice, rdfsDomain, CollectableClass),
  (aquirePrice, rdfsRange, XSD['decimal']),
  (aquirePrice, rdfsLabel, Literal('Acquire Price')),
  (aquirePrice, RDFS['comment'], Literal('Cost to acquire the item.')),

  (valuation, rdfType, owlObjectProperty),
  (valuation, displayOrder, Literal('5')),
  (valuation, rdfsDomain, CollectableClass),
  (valuation, rdfsRange, valuationClass),
  (valuation, rdfsLabel, Literal('Valuation')),
  (valuation, RDFS['comment'], Literal('Value of the item on a certain date.')),

  (tagContainer, rdfType, RDF['Seq']),
  (tagContainer, displayOrder, Literal('6')),
  (tagContainer, rdfsDomain, CollectableClass),
  (tagContainer, rdfsRange, XSD['string']),
  (tagContainer, rdfsLabel, Literal('Tags')),
  (tagContainer, RDFS['comment'], Literal('A list of keywords of your choosing that you use to identify, classify, characterize items.')),
  
  (basketClass, rdfType, owlClass),
  (basketClass, rdfsLabel, Literal('Basket')),
  (basketClass, rdfsSubClassOf, CollectableClass),
  (basketClass, isDefinedBy, catalogitLiteral),
  (basketClass, isUsedFor, usedForPrimary),

  (rugClass, rdfType, owlClass),
  (rugClass, rdfsSubClassOf, CollectableClass),
  (rugClass, rdfsLabel, Literal('Rug')),
  (rugClass, isDefinedBy, catalogitLiteral),
  (rugClass, isUsedFor, usedForPrimary),

  (maskClass, rdfType, owlClass),
  (maskClass, rdfsSubClassOf, CollectableClass),
  (maskClass, rdfsLabel, Literal('Mask')),
  (maskClass, isDefinedBy, catalogitLiteral),
  (maskClass, isUsedFor, usedForPrimary),

  (dollClass, rdfType, owlClass),
  (dollClass, rdfsSubClassOf, CollectableClass),
  (dollClass, rdfsLabel, Literal('Doll')),
  (dollClass, isDefinedBy, catalogitLiteral),
  (dollClass, isUsedFor, usedForPrimary),

  (carvedStoneClass, rdfType, owlClass),
  (carvedStoneClass, rdfsSubClassOf, CollectableClass),
  (carvedStoneClass, rdfsLabel, Literal('Carved Stone')),
  (carvedStoneClass, isDefinedBy, catalogitLiteral),
  (carvedStoneClass, isUsedFor, usedForPrimary),

  (pipeClass, rdfType, owlClass),
  (pipeClass, rdfsSubClassOf, CollectableClass),
  (pipeClass, rdfsLabel, Literal('Pipe')),
  (pipeClass, isDefinedBy, catalogitLiteral),
  (pipeClass, isUsedFor, usedForPrimary),
  
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

sg.commit()


#lifeLoggerNS = Namespace(BASE_GRAPH_URI + '_lifelogger/')
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
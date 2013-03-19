from rdflib import URIRef, Namespace, ConjunctiveGraph

from rdflib import RDFS, RDF, OWL, XSD

g = ConjunctiveGraph()

SELF = URIRef('http://catalogit.howardburrows.com')

rdf_type_predicate = RDF['type']


FBASE = Namespace("http://rdf.freebase.com/hs/")

FOAF = Namespace('http://xmlns.com/foaf/0.1/')

g.load('http://xmlns.com/foaf/spec/20100809.rdf')

DC = Namespace('http://purl.org/dc/elements/1.1/')

dc_creator = DC['creator']
dc_date = DC['date']
dc_description = DC['description']
dc_identifier = DC['identifier']
dc_subject = DC['subject']
cd_title = DC['title']

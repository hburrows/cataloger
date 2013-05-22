PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcmi: <http://purl.org/dc/dcmitype/>

PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>

PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

PREFIX common: <http://example.com/rdf/schemas/>

CLEAR GRAPH common: ;

# RDF and RDFS
LOAD <http://www.w3.org/2000/01/rdf-schema> INTO GRAPH common: ;
LOAD <http://www.w3.org/1999/02/22-rdf-syntax-ns> INTO GRAPH common: ;

# owl
LOAD <http://www.w3.org/2002/07/owl> INTO GRAPH common: ;

# ordered list ontology
LOAD <http://purl.org/ontology/olo/core> INTO GRAPH common: ; 

# DC vocabularies
LOAD <http://purl.org/dc/elements/1.1/> INTO GRAPH common: ;
LOAD <http://purl.org/dc/terms/> INTO GRAPH common: ;
LOAD <http://purl.org/dc/dcmitype/> INTO GRAPH common: ;

# FOAF
LOAD <http://xmlns.com/foaf/spec/20100809.rdf> INTO GRAPH common: ;

# VCARD
# LOAD <http://www.w3.org/2006/vcard/ns> INTO GRAPH common: ;

# GEO - i.e. latitude and longitude
LOAD <http://www.w3.org/2003/01/geo/wgs84_pos> INTO GRAPH common: ;

INSERT DATA {

  GRAPH common: {
  
  common:displayOrder rdf:type owl:DatatypeProperty .
  common:displayOrder rdfs:domain owl:DatatypeProperty .
  common:displayOrder rdfs:range xsd:integer .

  common:embed rdf:type owl:DatatypeProperty .
  common:embed rdf:domain owl:DatatypeProperty .
  common:embed rdfs:range xsd:boolean .
  
  common:StillImage rdf:type owl:Class .
  common:StillImage rdfs:label 'Still Image' .
  common:StillImage common:isUsedFor 'secondary' .
  common:StillImage common:embed true .
 
  common:location rdf:type owl:ObjectProperty .
  common:location rdfs:domain common:StillImage .
  common:location rdfs:range geo:Point .
  common:location rdfs:label 'Location' .
  
  common:images rdf:type rdf:Seq .
  common:images rdfs:label 'Images at different resolutions' .
  common:images rdfs:domain common:StillImage .
  common:images common:embed true .

  common:stillImageType rdf:type owl:DatatypeProperty .
  common:stillImageType rdfs:domain dcmi:StillImage .
  common:stillImageType rdfs:range xsd:string .
  
  common:stillImageURL rdf:type owl:DatatypeProperty .
  common:stillImageURL rdfs:domain dcmi:StillImage .
  common:stillImageURL rdfs:range xsd:string .
  
  common:stillImageWidth rdf:type owl:DatatypeProperty .
  common:stillImageWidth rdfs:domain dcmi:StillImage .
  common:stillImageWidth rdfs:range xsd:integer .
  
  common:stillImageHeight rdf:type owl:DatatypeProperty .
  common:stillImageHeight rdfs:domain dcmi:StillImage .
  common:stillImageHeight rdfs:range xsd:integer .
  
  # cit class declarations
  #
  common:Entry rdf:type owl:Class .
  #common:Entry rdfs:subClassOf owl:Thing .  
  common:Entry rdfs:label 'Entry' .
  common:Entry common:isDefinedBy 'catalogit' .

  common:createTime rdf:type owl:DatatypeProperty .
  common:createTime common:displayOrder 1 .
  common:createTime rdfs:domain common:Entry .
  common:createTime rdfs:range xsd:dateTime .
  common:createTime rdfs:label 'Create Time' .
  common:createTime rdfs:comment 'Date and time entry was entered into catalog.' .

  common:updateTime rdf:type owl:DatatypeProperty .
  common:updateTime common:displayOrder 2 .
  common:updateTime rdfs:domain common:Entry .
  common:updateTime rdfs:range xsd:dateTime .
  common:updateTime rdfs:label 'Update Time' .
  common:updateTime rdfs:comment 'Date and time entry was last updated.' .

  common:media rdf:type rdf:Seq .
  common:media common:displayOrder 3 .
  common:media rdfs:domain common:Entry .
  common:media rdfs:range common:StillImage .
  common:media rdfs:label 'Media Container' .
  common:media rdfs:comment 'The set of media (images videos sounds documents etc.) associated with the item.' .
  common:media common:embed true .

  common:tags rdf:type rdf:Seq .
  common:tags common:displayOrder 6 .
  common:tags rdfs:domain common:Entry .
  common:tags rdfs:range xsd:string .
  common:tags rdfs:label 'Tags' .
  common:tags rdfs:comment 'A list of keywords of your choosing that you use to identify classify characterize items.' .

  ###
  ### Experimental.  So an entry can have multiple parents need to define a class of: subClassOf, graphURI
  ###
  common:subClassGraph rdf:type owl:ObjectProperty .
  common:subClassGraph rdfs:domain common:Entry .
  common:subClassGraph rdfs:label 'Superclass Graph' .
  common:subClassGraph rdfs:comment 'URI that identifies the graph where the definition of the super class can be found.' .
  
  common:isUsedFor rdf:type owl:DatatypeProperty .
  common:isUsedFor rdfs:domain common:Entry .
  common:isUsedFor rdfs:label 'A tag used to indicate how a class is used.' .

	common:enumeration rdf:type rdf:Seq .
  common:enumeration rdfs:range xsd:string .
  common:enumeration rdfs:label 'A list of values the subject must equal' .

  foaf:Image common:isUsedFor 'secondary' .
  foaf:Agent common:isUsedFor 'secondary' .

  foaf:Person common:isUsedFor 'primary' .
  dcterms:Location common:isUsedFor 'secondary' .
  dcterms:BibliographicResource common:isUsedFor 'secondary' .
  foaf:Organization common:isUsedFor 'secondary' .
  
  foaf:Agent common:isUsedFor 'secondary' .
  <http://www.w3.org/2000/10/swap/pim/contact%23Person> common:isUsedFor 'secondary' .
  }
}

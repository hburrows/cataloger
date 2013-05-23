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

PREFIX : <http://example.com/rdf/schemas/>

CLEAR GRAPH : ;

# RDF and RDFS
LOAD <http://www.w3.org/2000/01/rdf-schema> INTO GRAPH : ;
LOAD <http://www.w3.org/1999/02/22-rdf-syntax-ns> INTO GRAPH : ;

# owl
LOAD <http://www.w3.org/2002/07/owl> INTO GRAPH : ;

# ordered list ontology
LOAD <http://purl.org/ontology/olo/core> INTO GRAPH : ; 

# DC vocabularies
LOAD <http://purl.org/dc/elements/1.1/> INTO GRAPH : ;
LOAD <http://purl.org/dc/terms/> INTO GRAPH : ;
LOAD <http://purl.org/dc/dcmitype/> INTO GRAPH : ;

# FOAF
LOAD <http://xmlns.com/foaf/spec/20100809.rdf> INTO GRAPH : ;

# VCARD
# LOAD <http://www.w3.org/2006/vcard/ns> INTO GRAPH : ;

# GEO - i.e. latitude and longitude
LOAD <http://www.w3.org/2003/01/geo/wgs84_pos> INTO GRAPH : ;

INSERT DATA {

  GRAPH : {
 
  # position property takes in form layout
  :displayOrder rdf:type owl:DatatypeProperty .
  :displayOrder rdfs:domain owl:DatatypeProperty .
  :displayOrder rdfs:range xsd:integer .

  # to embed full definition of objects
  :embed rdf:type owl:DatatypeProperty .
  :embed rdf:domain owl:DatatypeProperty .
  :embed rdfs:range xsd:boolean .
  
  # to force object to be bnode
  :bnode rdf:type owl:DatatypeProperty .
  :bnode rdf:domain owl:DatatypeProperty .
  :bnode rdfs:range xsd:boolean .
  
  :StillImage rdf:type owl:Class .
  :StillImage rdfs:label 'Still Image' .
  :StillImage :isUsedFor 'secondary' .
  :StillImage :embed true .
 
  :location rdf:type owl:ObjectProperty .
  :location rdfs:domain :StillImage .
  :location rdfs:range geo:Point .
  :location rdfs:label 'Location' .
  :location :bnode true .
  
  :images rdf:type rdf:Seq .
  :images rdfs:label 'Images at different resolutions' .
  :images rdfs:domain :StillImage .
  :images :bnode true .

  :stillImageType rdf:type owl:DatatypeProperty .
  :stillImageType rdfs:domain dcmi:StillImage .
  :stillImageType rdfs:range xsd:string .
  
  :stillImageURL rdf:type owl:DatatypeProperty .
  :stillImageURL rdfs:domain dcmi:StillImage .
  :stillImageURL rdfs:range xsd:string .
  
  :stillImageWidth rdf:type owl:DatatypeProperty .
  :stillImageWidth rdfs:domain dcmi:StillImage .
  :stillImageWidth rdfs:range xsd:integer .
  
  :stillImageHeight rdf:type owl:DatatypeProperty .
  :stillImageHeight rdfs:domain dcmi:StillImage .
  :stillImageHeight rdfs:range xsd:integer .
  
  # cit class declarations
  #
  :Entry rdf:type owl:Class .
  #:Entry rdfs:subClassOf owl:Thing .  
  :Entry rdfs:label 'Entry' .
  :Entry :isDefinedBy 'catalogit' .

  :createTime rdf:type owl:DatatypeProperty .
  :createTime :displayOrder 1 .
  :createTime rdfs:domain :Entry .
  :createTime rdfs:range xsd:dateTime .
  :createTime rdfs:label 'Create Time' .
  :createTime rdfs:comment 'Date and time entry was entered into catalog.' .

  :updateTime rdf:type owl:DatatypeProperty .
  :updateTime :displayOrder 2 .
  :updateTime rdfs:domain :Entry .
  :updateTime rdfs:range xsd:dateTime .
  :updateTime rdfs:label 'Update Time' .
  :updateTime rdfs:comment 'Date and time entry was last updated.' .

  :media rdf:type rdf:Seq .
  :media :displayOrder 3 .
  :media rdfs:domain :Entry .
  :media rdfs:range :StillImage .
  :media rdfs:label 'Media Container' .
  :media rdfs:comment 'The set of media (images videos sounds documents etc.) associated with the item.' .
  :media :embed true .

  :tags rdf:type rdf:Seq .
  :tags rdfs:label 'Tags' .
  :tags rdfs:comment 'A list of keywords of your choosing that you use to identify classify characterize items.' .
  :tags rdfs:domain :Entry .
  :tags rdfs:range xsd:string .
  :tags :bnode true .
  :tags :displayOrder 6 .

  ###
  ### Experimental.  So an entry can have multiple parents need to define a class of: subClassOf, graphURI
  ###
  :subClassGraph rdf:type owl:ObjectProperty .
  :subClassGraph rdfs:domain :Entry .
  :subClassGraph rdfs:label 'Superclass Graph' .
  :subClassGraph rdfs:comment 'URI that identifies the graph where the definition of the super class can be found.' .
  
  :isUsedFor rdf:type owl:DatatypeProperty .
  :isUsedFor rdfs:domain :Entry .
  :isUsedFor rdfs:label 'A tag used to indicate how a class is used.' .

	:enumeration rdf:type rdf:Seq .
  :enumeration rdfs:range xsd:string .
  :enumeration rdfs:label 'A list of values the subject must equal' .

	# Mark loaded classes as primary/secondary.
	#
  foaf:Image :isUsedFor 'secondary' .
  foaf:Agent :isUsedFor 'secondary' .
  foaf:Person :isUsedFor 'secondary' .
  foaf:Organization :isUsedFor 'secondary' .

  dcterms:Location :isUsedFor 'secondary' .
  dcterms:BibliographicResource :isUsedFor 'secondary' .
  
  <http://www.w3.org/2000/10/swap/pim/contact%23Person> :isUsedFor 'secondary' .
  }
}

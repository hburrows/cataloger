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

  ###
  ### Experimental.  So and entry can have multiple parents need to define a class of: subClassOf, graphURI
  ###
  common:subClassGraph rdf:type owl:ObjectProperty .
  common:subClassGraph rdfs:domain common:Entry .
  common:subClassGraph rdfs:label 'Superclass Graph' .
  common:subClassGraph rdfs:comment 'URI that identifies the graph where the definition of the super class can be found.' .
  
  common:isUsedFor rdf:type owl:DatatypeProperty .
  common:isUsedFor rdfs:domain common:Entry .
  common:isUsedFor rdfs:label 'A tag used to indicate how a class is used.' .

  common:Collectable rdf:type owl:Class .
  common:Collectable rdfs:subClassOf common:Entry .
  common:Collectable rdfs:label 'Collectable' .
  common:Collectable common:isDefinedBy 'catalogit' .
  common:Collectable common:isUsedFor 'primary' .

  # property and tenant class definitions
  #
  common:Valuation rdf:type owl:Class .
  common:Valuation rdfs:label 'Valuation' .
  common:Valuation common:isUsedFor 'secondary' .

  common:valuation.value rdf:type owl:DatatypeProperty .
  common:valuation.value common:displayOrder 1 .
  common:valuation.value rdfs:domain common:Valuation .
  common:valuation.value rdfs:range xsd:decimal .
  common:valuation.value rdfs:label 'Value' .
  common:valuation.value rdfs:comment 'Real or estimated value of item.' .
  
  common:valuation.date rdf:type owl:DatatypeProperty .
  common:valuation.date common:displayOrder 2 .
  common:valuation.date rdfs:domain common:Valuation .
  common:valuation.date rdfs:range xsd:dateTime .
  common:valuation.date rdfs:label 'Date' .
  common:valuation.date rdfs:comment 'Date valuation was provided.' .

  common:valuation.agent rdf:type owl:ObjectProperty .
  common:valuation.agent common:displayOrder 3 .
  common:valuation.agent rdfs:domain common:Valuation .
  common:valuation.agent rdfs:range foaf:Agent .
  common:valuation.agent rdfs:label 'Provider' .
  common:valuation.agent rdfs:comment 'Person or organization that provided the valuation.' .

  # properties of collectable
  dc:title rdfs:domain common:Collectable .
  dc:title common:displayOrder 1 .

  dc:description rdfs:domain common:Collectable .
  dc:description common:displayOrder 2 .

  common:aquireDate rdf:type owl:DatatypeProperty .
  common:aquireDate common:displayOrder 3 .
  common:aquireDate rdfs:domain common:Collectable .
  common:aquireDate rdfs:range xsd:dateTime .
  common:aquireDate rdfs:label 'Acquire Date' .
  common:aquireDate rdfs:comment 'Date the item was acquired.' .

  common:aquirePrice rdf:type owl:DatatypeProperty .
  common:aquirePrice common:displayOrder 4 .
  common:aquirePrice rdfs:domain common:Collectable .
  common:aquirePrice rdfs:range xsd:decimal .
  common:aquirePrice rdfs:label 'Acquire Price' .
  common:aquirePrice rdfs:comment 'Cost to acquire the item.' .

  common:valuationOn rdf:type owl:ObjectProperty .
  common:valuationOn common:displayOrder 5 .
  common:valuationOn rdfs:domain common:Collectable .
  common:valuationOn rdfs:range common:Valuation .
  common:valuationOn rdfs:label 'Valuation' .
  common:valuationOn rdfs:comment 'Value of the item on a certain date.' .

  common:tags rdf:type rdf:Seq .
  common:tags common:displayOrder 6 .
  common:tags rdfs:domain common:Collectable .
  common:tags rdfs:range xsd:string .
  common:tags rdfs:label 'Tags' .
  common:tags rdfs:comment 'A list of keywords of your choosing that you use to identify classify characterize items.' .
  
  common:Basket rdf:type owl:Class .
  common:Basket rdfs:label 'Basket' .
  common:Basket rdfs:subClassOf common:Collectable .
  common:Basket common:isDefinedBy 'catalogit' .
  common:Basket common:isUsedFor 'primary' .

  common:Rug rdf:type owl:Class .
  common:Rug rdfs:subClassOf common:Collectable .
  common:Rug rdfs:label 'Rug' .
  common:Rug common:isDefinedBy 'catalogit' .
  common:Rug common:isUsedFor 'primary' .

  common:Mask rdf:type owl:Class .
  common:Mask rdfs:subClassOf common:Collectable .
  common:Mask rdfs:label 'Mask' .
  common:Mask common:isDefinedBy 'catalogit' .
  common:Mask common:isUsedFor 'primary' .

  common:Doll rdf:type owl:Class .
  common:Doll rdfs:subClassOf common:Collectable .
  common:Doll rdfs:label 'Doll' .
  common:Doll common:isDefinedBy 'catalogit' .
  common:Doll common:isUsedFor 'primary' .

  common:CarvedStone rdf:type owl:Class .
  common:CarvedStone rdfs:subClassOf common:Collectable .
  common:CarvedStone rdfs:label 'Carved Stone' .
  common:CarvedStone common:isDefinedBy 'catalogit' .
  common:CarvedStone common:isUsedFor 'primary' .

  common:Pipe rdf:type owl:Class .
  common:Pipe rdfs:subClassOf common:Collectable .
  common:Pipe rdfs:label 'Pipe' .
  common:Pipe common:isDefinedBy 'catalogit' .
  common:Pipe common:isUsedFor 'primary' .
  
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

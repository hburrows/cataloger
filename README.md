# CatalogIt API Reference

## cataloger

### Principles
// universally represent everything as -- of which any property can be missing

    ID, VALUE, TYPE, SCHEMA

   OR

    ID, PREDICATE, DATA, SCHEMA

	 OR
	
	  ID <string>, TYPE <string>, DATA <dictionary>, SCHEMA <list>
			
			data: dictionary of predicate: values
	     - predicates are the keys to the 'data' dictionary
	     - values are either data-properties or object-properties.  Object properties have a recursive {id, type, data, schema} layout
	
			 - ??? values can be either strings/numbers, objects, or lists.  Multiple values are represented as lists
			
			schema: list



###  FRAGMENTS

		// individual image
		imageInstance: {
			type: 'http://purl.org/dc/dcmitype/StillImage',
			data: {
				type: 'thumbnail', 'low_resolution', 'medium_resolution', 'high_resolution'
				url: 'http://s3.amazon...',
				width: xsd:int,
				height: xsd:int
			}
		}

		"http://example.com/rdf/schemas/location": {
			type: http://www.w3.org/2003/01/geo/wgs84_pos#Point,
			data: {
				lat: 55.701,
				long: 12.552
			}
		}

		"http://example.com/rdf/schemas/images": {
			'type': 'http://example.com/rdf/schemas/StillImageSeq',
			'data': [ {type: 'http://purl.org/dc/dcmitype/StillImage', data: { type, url, width, height }}, {...} ]
		}


### Example 
		{
		  id: http://example.com/api/entries/24/
		  type: http://example.com/rdf/schemas/Doll
		  schema: {}
		  data: {

				"http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "http://example.com/rdf/schemas/Doll", 
				"http://example.com/rdf/schemas/createTime": "1363888433", 
				"http://purl.org/dc/elements/1.1/title": "Suzy", 
				"http://purl.org/dc/elements/1.1/description": "Sweetest girl on the block", 
				"http://example.com/rdf/schemas/updateTime": "1363888433", 
				"http://example.com/rdf/schemas/aquireDate": "45",

		    "http://example.com/rdf/schemas/media": {

					type: http://example.com/rdf/schemas/MediaContainer,   // StillImage, MovingImage, Sound
					schema: {}
					data: [ 

						{
							type: http://example.com/rdf/schemas/StillImage
							data: {

								"http://example.com/rdf/schemas/location": {
									type: http://www.w3.org/2003/01/geo/wgs84_pos#Point,
									data: {
										lat: 55.701,
										long: 12.552
									}
								}

								"http://example.com/rdf/schemas/images": {
									type: 'http://example.com/rdf/schemas/StillImageSeq',
									data: [ {type: 'http://purl.org/dc/dcmitype/StillImage', data: { type, url, width, height }}, {...} ]
								}
							}
						},

						{
							type: http://purl.org/dc/dcmitype/MovingImage
							data: { ... }
						},

						...

					]
				}
			}
		}
				
							
### Obsolete

    // [] are seqs, http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq, // [] are bags, http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag


    "id": "http%3A//example.com/rdf/users/2%239", 
    "schema": [
        {
            "comment": "", 
            "name": "Doll", 
            "properties": [], 
            "classUri": "http%3A//example.com/rdf/schemas/Doll", 
            "id": "http%3A//example.com/rdf/schemas/Doll"
        }, 
        {
            "comment": "", 
            "name": "Collectable", 
            "properties": [
                {
                    "comment": "A name given to the resource.", 
                    "ancestors": [], 
                    "label": "Title", 
                    "range": null, 
                    "property": "http://purl.org/dc/elements/1.1/title", 
                    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
                }, 
                {
                    "comment": "An account of the resource.", 
                    "ancestors": [], 
                    "label": "Description", 
                    "range": null, 
                    "property": "http://purl.org/dc/elements/1.1/description", 
                    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
                }, 
                {
                    "comment": "Date the item was acquired.", 
                    "ancestors": [], 
                    "label": "Acquire Date", 
                    "range": "http://www.w3.org/2001/XMLSchema#date", 
                    "property": "http://example.com/rdf/schemas/aquirePrice", 
                    "type": "http://www.w3.org/2002/07/owl#DatatypeProperty"
                }, 
                {
                    "comment": "Cost to acquire the item.", 
                    "ancestors": [], 
                    "label": "Acquire Price", 
                    "range": "http://www.w3.org/2001/XMLSchema#decimal", 
                    "property": "http://example.com/rdf/schemas/aquireDate", 
                    "type": "http://www.w3.org/2002/07/owl#DatatypeProperty"
                }, 
                {
                    "comment": "Value of the item on a certain date.", 
                    "ancestors": [], 
                    "label": "Valuation", 
                    "range": "http://example.com/rdf/schemas/Valuation", 
                    "property": "http://example.com/rdf/schemas/valuationOn", 
                    "type": "http://www.w3.org/2002/07/owl#ObjectProperty"
                }, 
                {
                    "comment": "A list of keywords of your choosing that you use to identify, classify, characterize items.", 
                    "ancestors": [
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag", 
                        "http://www.w3.org/2000/01/rdf-schema#Container", 
                        "http://www.w3.org/2000/01/rdf-schema#Resource"
                    ], 
                    "label": "Tags", 
                    "range": "http://example.com/rdf/schemas/TagContainer", 
                    "property": "http://example.com/rdf/schemas/tagContainer", 
                    "type": "http://www.w3.org/2002/07/owl#ObjectProperty"
                }
            ], 
            "classUri": "http%3A//example.com/rdf/schemas/Collectable", 
            "id": "http%3A//example.com/rdf/schemas/Collectable"
        }, 
        {
            "comment": "", 
            "name": "Entry", 
            "properties": [
                {
                    "comment": "Date and time entry was entered into catalog.", 
                    "ancestors": [], 
                    "label": "Create Time", 
                    "range": "http://www.w3.org/2001/XMLSchema#dateTime", 
                    "property": "http://example.com/rdf/schemas/createTime", 
                    "type": "http://www.w3.org/2002/07/owl#DatatypeProperty"
                }, 
                {
                    "comment": "Date and time entry was last updated.", 
                    "ancestors": [], 
                    "label": "Update Time", 
                    "range": "http://www.w3.org/2001/XMLSchema#dateTime", 
                    "property": "http://example.com/rdf/schemas/updateTime", 
                    "type": "http://www.w3.org/2002/07/owl#DatatypeProperty"
                }, 
                {
                    "comment": "The set of media (images, videos, sounds, documents, etc.) associated with the item.", 
                    "ancestors": [
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq", 
                        "http://www.w3.org/2000/01/rdf-schema#Container", 
                        "http://www.w3.org/2000/01/rdf-schema#Resource"
                    ], 
                    "label": "Media Container", 
                    "range": "http://example.com/rdf/schemas/MediaContainer", 
                    "property": "http://example.com/rdf/schemas/media", 
                    "type": "http://www.w3.org/2002/07/owl#ObjectProperty"
                }
            ], 
            "classUri": "http%3A//example.com/rdf/schemas/Entry", 
            "id": "http%3A//example.com/rdf/schemas/Entry"
        }
    ]

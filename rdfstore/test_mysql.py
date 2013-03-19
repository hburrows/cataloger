'''
Created on Mar 8, 2013

@author: howard
'''

import rdflib
from rdflib import ConjunctiveGraph, Graph
from rdflib import plugin
from rdflib.store import Store
from rdflib.store import VALID_STORE
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from pprint import pprint

from globals import DEFAULT_GRAPH_URI, DB, _get_mysql_config_string

# Get the mysql plugin. You may have to install the python mysql libraries

store = plugin.get('MySQL', Store)(DB)
store.open(_get_mysql_config_string(),create=False)

g = ConjunctiveGraph(store)

rs = g.query(
"""
PREFIX cit: <http://example.com/rdf/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?class ?label
WHERE {
 ?class rdf:type owl:Class .
}
"""
)

for r in rs:
  print r

rs = g.query(
"""
SELECT ?node ?attr ?val
WHERE { ?node ?attr ?val }
ORDER BY ?node
"""
)

for r in rs:
  print r

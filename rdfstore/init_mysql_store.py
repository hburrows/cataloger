'''
Created on Mar 7, 2013

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

from globals import DEFAULT_GRAPH_URI, _get_mysql_config_string


# There is a store, use it
citg = ConjunctiveGraph('MySQL', identifier=URIRef(DEFAULT_GRAPH_URI))

rt = citg.open(_get_mysql_config_string(), create=True)

assert rt == VALID_STORE,"The underlying store is corrupted"

citg.commit()

citg.close()



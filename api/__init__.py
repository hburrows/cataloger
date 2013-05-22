'''
Created on Mar 21, 2013

@author: howard
'''

from rdflib import URIRef
from rdflib import OWL, RDFS

BASE_GRAPH_URI = "http://example.com/rdf/"

SCHEMA_GRAPH_URI = BASE_GRAPH_URI + 'schemas/'
COMMON_GRAPH_URI = BASE_GRAPH_URI + 'schemas/'

USER_GRAPH_URI = BASE_GRAPH_URI + 'users/{userId}/'

REQUIRED_VOCABULARIES = [
    'http://example.com/rdf/schemas/'
]

DEFAULT_VOCABULARIES = [
    'http://example.com/rdf/schemas/community/life_events/'
]

MYSQL_HOST = 'localhost'
POSTGRES_HOST = '/tmp/'
USER = 'howard'
PASSWORD = 'd#vel0p'
DB = 'rdfstore'

'''
  DATABASE
'''
def _get_mysql_config_string():
  return 'host={0},user={1},password={2},db={3}'.format(MYSQL_HOST, USER, PASSWORD, DB)

def _get_postgresql_config_string():
  return 'host={0} user={1} dbname={2}'.format(POSTGRES_HOST, USER, DB)

def _get_bsddb_config_string():
  return '/Users/howard/dev/catalogit/cataloger/bsddb'

def _get_sqlalchemy_config_string():
  return 'mysql://{user}:{password}@{host}/{database}?charset=utf8'.format(user=USER, password=PASSWORD, host=MYSQL_HOST, database=DB)

#DATABASE_STORE = 'MySQL'
#_get_db_config_string = _get_mysql_config_string
                                                                             
#DATABASE_STORE = 'PostgreSQL'
#_get_db_config_string = _get_postgresql_config_string

DATABASE_STORE = 'Sleepycat'
_get_db_config_string = _get_bsddb_config_string

#DATABASE_STORE = 'SQLAlchemy'
#_get_db_config_string = _get_sqlalchemy_config_string


'''
Created on Mar 7, 2013

@author: howard
'''

'''
  Use sub-paths of 'class', 'resource', 'property'
'''
DEFAULT_GRAPH_URI = "http://example.com/rdf/"

SCHEMA_GRAPH_URI = DEFAULT_GRAPH_URI + 'schemas/'

MYSQL_HOST = 'localhost'
POSTGRES_HOST = '/tmp/'
USER = 'howard'
PASSWORD = 'd#vel0p'
DB = 'rdfstore'

def _get_mysql_config_string():
  return 'host={0},user={1},password={2},db={3}'.format(MYSQL_HOST, USER, PASSWORD, DB)

def _get_postgresql_config_string():
  return 'host={0} user={1} dbname={2}'.format(POSTGRES_HOST, USER, DB)

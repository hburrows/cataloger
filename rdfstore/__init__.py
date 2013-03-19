

DEFAULT_GRAPH_URI = "http://example.com/rdfstore"

HOST = 'localhost'
USER = 'howard'
PASSWORD = 'd#vel0p'
DB = 'rdfstore'

def _get_config_string():
  return 'host={0},user={1},password={2},db={3}'.format(HOST, USER, PASSWORD, DB)

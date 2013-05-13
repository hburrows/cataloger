'''
Created on Apr 26, 2013

@author: howard
'''


from piston.handler import BaseHandler
from piston.utils import rc

from api import SCHEMA_GRAPH_URI

from . import sparql_froms_for_user, sparql_query

class UserClassesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'DELETE')

  def read(self, request, user_id, subject_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:

      template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX common: <{sg}>
SELECT DISTINCT ?class ?label ?comment
{graphs}
WHERE {{
  ?class rdf:type owl:Class .
  ?class common:isUsedFor "primary" 
  OPTIONAL {{ ?class rdfs:label ?label . }}
  OPTIONAL {{ ?class rdfs:comment ?comment . }}
}}
ORDER BY (?label)
'''
      rq = template.format(sg=SCHEMA_GRAPH_URI,graphs=sparql_froms_for_user(request.user))

      classes = []
      for result in sparql_query(rq)["results"]["bindings"]:
  
        cls = result['class']['value']
        label = result['label']['value'] if 'label' in result else None
        comment = result['comment']['value'] if 'comment' in result else None
        
        classes.append({
          'id': cls,
          'name': label,
          'comment': comment,
        })

    finally:
      pass

    return classes


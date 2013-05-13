'''
Created on Mar 8, 2013

@author: howard
'''

from django.conf import settings

from piston.handler import BaseHandler

from api import SCHEMA_GRAPH_URI
from api.models import Graph

from . import sparql_query, sparql_froms_for_user

class ClassesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  def read(self, request, class_id=None):
    
    try:

      template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX sg: <{sg}>
SELECT DISTINCT ?class ?label ?comment
{graphs}
WHERE {{
  ?class rdf:type owl:Class .
  ?class sg:isUsedFor "primary" 
  OPTIONAL {{ ?class rdfs:label ?label . }}
  OPTIONAL {{ ?class rdfs:comment ?comment . }}
}}
ORDER BY (?label)
'''
      rq = template.format(sg=SCHEMA_GRAPH_URI,graphs=' '.join(['FROM <' + g.graph_uri + '>' for g in Graph.objects.all()]))

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

  def create(self, request):
    pass


  
  
  
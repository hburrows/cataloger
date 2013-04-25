'''
Created on Mar 8, 2013

@author: howard
'''

from django.conf import settings

from piston.handler import BaseHandler

from api import SCHEMA_GRAPH_URI

from . import sparql_query

#from api.models import User

class ClassesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id=None):
    
    try:

      template = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX sg: <{sg}>
SELECT ?class ?label ?comment
FROM NAMED <{sg}>
WHERE {{
  GRAPH <{sg}>
  {{
    {{ 
      ?class rdf:type owl:Class .
      ?class sg:isUsedFor "primary" 
      OPTIONAL {{ ?class rdfs:label ?label . }}
      OPTIONAL {{ ?class rdfs:comment ?comment . }}
    }}
    UNION
    {{
      ?class rdf:type rdfs:Class .
      ?class sg:isUsedFor "primary" 
      OPTIONAL {{ ?class rdfs:label ?label . }}
      OPTIONAL {{ ?class rdfs:comment ?comment . }}
    }}
  }}
}}
ORDER BY (?label)
'''
      rq = template.format(sg=SCHEMA_GRAPH_URI)

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


  
  
  
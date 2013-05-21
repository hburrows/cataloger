'''
Created on May 8, 2013

@author: howard
'''

from piston.handler import BaseHandler

from api.models import Graph


class GraphsHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id=None):
    return [{'graph_uri': g.graph_uri, 'label': g.label} for g in Graph.objects.all()]  

  def create(self, request):
    pass


  
  
  
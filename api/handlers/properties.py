'''
Created on Mar 8, 2013

@author: howard
'''

from piston.handler import BaseHandler
from piston.utils import rc

from . import get_full_schema_for, sparql_graphs_for_user

class PropertiesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id):

    try:

      result = get_full_schema_for(sparql_graphs_for_user(request.user), class_id)

    except Exception, e:
      import traceback
      print traceback.format_exc()
      raise e

    return result
  

  def create(self, request):
    pass


  
  
  
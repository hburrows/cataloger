'''
Created on Mar 8, 2013

@author: howard
'''

from piston.handler import BaseHandler
from piston.utils import rc

from . import get_full_schema_for

class PropertiesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, class_id):

    try:

      result = get_full_schema_for(class_id)

    except Exception, e:
      resp = rc.BAD_REQUEST
      resp.write('.  Error {0}'.format(e))
      return resp

    return result
  

  def create(self, request):
    pass


  
  
  
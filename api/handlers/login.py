'''
Created on Oct 20, 2012

@author: howard
'''

import json

from django.contrib.auth import authenticate, login, logout

from piston.handler import BaseHandler
from piston.utils import rc


class LoginHandler(BaseHandler):

  allowed_methods = ('POST')

  def create(self, request):

    try:
      body_obj = json.loads(request.body)
      
      username = body_obj.get('username')
      password = body_obj.get('password')

    except:
      return rc.BAD_REQUEST
  
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        return user
      else:
        return rc.NOT_IMPLEMENTED
        return {'error': 'account disabled'}
    else:
      resp = rc.FORBIDDEN
      #resp['Content-Type'] = 'application/json; charset=utf-8'
      resp.write(' - Invalid credentials')
      return resp
        
  
class LogoutHandler(BaseHandler):

  allowed_methods = ('POST')

  def create(self, request):
    logout(request)
    return {}
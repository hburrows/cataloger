'''
Created on Oct 19, 2012

@author: howard
'''

import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import IntegrityError

from piston.handler import BaseHandler
from piston.utils import rc


#from api.models import User

class UsersHandler(BaseHandler):

  allowed_methods = ('GET', 'POST')

  #fields = ('name', 'email')
  
  def read(self, request, user_id=None):

    if user_id:

      # details for one user
      if user_id.lower() == 'self':
        user_id = request.user.id

      # can only view your own data unless you're a superuser
      if not request.user.is_superuser and int(user_id) != request.user.id:
        return rc.FORBIDDEN

      user = get_object_or_404(User, pk=user_id)
      return user

    else:
      # list all users
      if not request.user.is_superuser:
        return rc.FORBIDDEN
      post = User.objects.all()
      return post

  def create(self, request):
    
    try:

      body_obj = json.loads(request.body)
      
      username = body_obj.get('username')
      password = body_obj.get('password')
      email = body_obj.get('email')
      
      first_name = body_obj.get('first_name', None)
      last_name = body_obj.get('last_name', None)

    except:
      return rc.BAD_REQUEST

    try:
      user = User.objects.create_user(username, email, password)

    except IntegrityError:
      resp = rc.DUPLICATE_ENTRY
      resp.write('.  That username is already taken.  Please try another username.')
      return resp

    try:

      saveUser = False
      
      if first_name:
        user.first_name  = first_name
        saveUser = True
      if last_name:
        user.last_name = last_name
        saveUser = True
      
      if saveUser:
        user.save()

    except:
      pass

    return user

  def update(self, request, user_id):

    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only delete your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:

      body_obj = json.loads(request.body)
      
      password = body_obj.get('password', None)

    except:
      return rc.BAD_REQUEST

    if password:
      request.user.set_password(password)
      request.user.save()

    return {}
    
  def delete(self, request, user_id):

    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only delete your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    request.user.delete()
    request.user.save()

    return request.user

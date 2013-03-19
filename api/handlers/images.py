'''
Created on Mar 14, 2013

@author: howard
'''

import json

from django.shortcuts import get_object_or_404

from piston.handler import BaseHandler
from piston.utils import rc

from api.models import Image
from api.forms import ImageForm

class UserImagesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  # fields = ('name', 'email')
  
  def read(self, request, user_id, image_id):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    image = get_object_or_404(Image, pk=image_id)
    return image.to_json_obj()

  def create(self, request, user_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:

      form = ImageForm(request.POST, request.FILES)
      if not form.is_valid():
        return rc.BAD_REQUEST;

    except Exception, e:
      return rc.BAD_REQUEST

    try:
      image = Image(user_id=user_id, image=request.FILES['image'])
      image.save()
    except Exception, e:
      import traceback
      traceback.print_exc()
      resp = rc.INTERNAL_ERROR
      resp.write(' - ' + str(e))
      return resp

    return image.to_json_obj()
  
  def update(self, request, user_id, entry_id, image_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    try:
      body_obj = json.loads(request.body)
    except:
      return rc.BAD_REQUEST

    activity = get_object_or_404(Image, pk=entry_id)

    if body_obj.get('activity_type'):
      activity.activity_type = body_obj.get('activity_type')
    if body_obj.get('activity_time'):
      activity.activity_time = body_obj.get('activity_time')
    if body_obj.get('attributes'):
      activity.attributes = body_obj.get('attributes')

    activity.save()
    
    return activity.to_json_obj() 

  def delete(self, request, user_id, entry_id, image_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    activity = get_object_or_404(Image, pk=entry_id)
    
    activity.delete()

    return activity.to_json_obj()

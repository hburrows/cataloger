'''
Created on Mar 14, 2013

@author: howard
'''

import os
import tempfile

from django.shortcuts import get_object_or_404
from django.core.files import File

from piston.handler import BaseHandler
from piston.utils import rc

from PIL import Image

from api.models import Image as ImageModel, THUMBNAIL_SIZE

from api.forms import ImageForm

class UserImagesHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  def read(self, request, user_id, image_id):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    image = get_object_or_404(ImageModel, pk=image_id)
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
      originalImage = request.FILES['image']

      extension = os.path.splitext(originalImage.name)[1][1:]

      im = Image.open(originalImage)
      
      im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

      thumbnail = File(tempfile.TemporaryFile(mode='w+b'))

      im.save(thumbnail, extension)

      image = ImageModel(user_id=user_id, image=originalImage, original=originalImage, thumbnail=thumbnail)
      image.save()

      thumbnail.close()

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
      #body_obj = json.loads(request.body)
      pass
    except:
      return rc.BAD_REQUEST

    image = get_object_or_404(ImageModel, pk=entry_id)

    image.save()
    
    return image.to_json_obj() 

  def delete(self, request, user_id, entry_id, image_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    image = get_object_or_404(ImageModel, pk=entry_id)
    
    image.delete()

    return image.to_json_obj()

'''
Created on Oct 19, 2012

@author: howard
'''

import logging


from piston.handler import BaseHandler
from piston.utils import rc

logger = logging.getLogger(__name__)

class UserEntryHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

  fields = ('name', 'email')

  def _get_image_json_obj(self, entry):
    images_obj = []
    images = entry.entryimage_set.all()
    if images:
      for image in images:
        images_obj.append(image.to_json_obj());
    return images_obj
    
  def read(self, request, user_id, entry_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    if entry_id:
      return {}
    else:
      return []

  def create(self, request, user_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only create your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    try:
      #body_obj = json.loads(request.body)
      pass

    except:
      return rc.BAD_REQUEST

    return {}
  
  def update(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only update your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    try:
      #body_obj = json.loads(request.body)
      pass

    except:
      return rc.BAD_REQUEST

    return {}

  def delete(self, request, user_id, entry_id):
  
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id
    
    # can only delete your own entries
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN
    
    return {}

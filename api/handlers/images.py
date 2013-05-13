'''
Created on Mar 14, 2013

@author: howard
'''

import os
import tempfile
import uuid

from django.shortcuts import get_object_or_404
from django.core.files import File

from piston.handler import BaseHandler
from piston.utils import rc

from PIL import Image

from rdflib import Namespace

from api import USER_GRAPH_URI, COMMON_GRAPH_URI
from api.models import Image as ImageModel, THUMBNAIL_SIZE
from api.forms import ImageForm

from . import sparql_update, sparql_froms_for_user

import rdfutils

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

    USER = Namespace(str(USER_GRAPH_URI).format(userId=user_id))

    subject_uuid = uuid.uuid4().hex
    subject_url = USER[subject_uuid]
    
    try:
      originalImage = request.FILES['image']

      extension = os.path.splitext(originalImage.name)[1][1:]

      im = Image.open(originalImage)
      
      im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

      thumbnail = File(tempfile.TemporaryFile(mode='w+b'))

      im.save(thumbnail, extension)

      image = ImageModel(user_id=user_id, image_url=subject_url, original=originalImage, thumbnail=thumbnail)
      image.save()

      thumbnail.close()

    except Exception, e:
      import traceback
      traceback.print_exc()
      resp = rc.INTERNAL_ERROR
      resp.write(' - ' + str(e))
      return resp

    ru_tmpl = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX dcmi: <http://purl.org/dc/dcmitype/>
PREFIX common: <{cg_uri}>
PREFIX : <{ug_url}>
INSERT DATA {{
  GRAPH : {{
    :{subject_uuid}
      rdf:type common:StillImage ;
      common:location [
        rdf:type geo:Point ;
        geo:long {geo_long} ;
        geo:lat {geo_lat} ;
      ] ;
      common:images [
        rdf:type rdf:Seq ;
        rdf:_1 [
          rdf:type dcmi:StillImage ;
          common:stillImageType "original" ;
          common:stillImageURL "{original_image_url}" ;
          common:stillImageWidth {original_image_width} ;
          common:stillImageHeight {original_image_height} ;
        ] ;
        rdf:_2 [
          rdf:type dcmi:StillImage ;
          common:stillImageType "thumbnail" ;
          common:stillImageURL "{thumbnail_image_url}" ;
          common:stillImageWidth {thumbnail_image_width} ;
          common:stillImageHeight {thumbnail_image_height} ;
        ] ;
      ] .
  }}
}}'''

    ru = ru_tmpl.format(
      cg_uri=COMMON_GRAPH_URI,
      ug_url=str(USER),
      subject_uuid=subject_uuid,
      geo_long=0,
      geo_lat=0,
      original_image_url=image.original.url,
      original_image_width=image.original.width,
      original_image_height=image.original.height,
      thumbnail_image_url=image.thumbnail.url,
      thumbnail_image_width=image.thumbnail.width,
      thumbnail_image_height=image.thumbnail.height)

    sparql_update(ru)

    return rdfutils.object_to_json(sparql_froms_for_user(request.user), COMMON_GRAPH_URI, str(USER), USER[subject_uuid])
  
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

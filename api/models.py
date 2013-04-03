import os

from django.db import models
from django.contrib.auth.models import User

from storages.backends.s3boto import S3BotoStorage

from . import USER_GRAPH_URI

THUMBNAIL_SIZE = (60,60)


class UserProfile(models.Model):
  user = models.OneToOneField(User, primary_key=True)

  schema = models.TextField(max_length=128, null=True)


def original_pathname(model, filename):
  name, ext = os.path.splitext(filename)
  return 'users/{0}/{1}.original{2}'.format(model.user.id, name, ext)

def thumbnail_pathname(model, filename):
  original = os.path.basename(model.original.name)
  name, ext = os.path.splitext(original)
  return 'users/{0}/{1}.thumbnail{2}'.format(model.user.id, name.split('.')[0], ext)

class Image(models.Model):

  user = models.ForeignKey(User)

  original_width = models.IntegerField()
  original_height = models.IntegerField()
  original = models.ImageField(upload_to=original_pathname,
                               storage=S3BotoStorage(bucket='images.catalogit.howardburrows.com'),
                               width_field='original_width',
                               height_field='original_height')

  thumbnail_width = models.IntegerField()
  thumbnail_height = models.IntegerField()
  thumbnail = models.ImageField(upload_to=thumbnail_pathname,
                                storage=S3BotoStorage(bucket='images.catalogit.howardburrows.com'),
                                width_field='thumbnail_width',
                                height_field='thumbnail_height')

  def to_json_obj(self):
    return {'id': self.id,
            'user_id': self.user.id,
            'original': {
              'url': self.original.url,
              'type': 'original',
              'width': self.original_width,
              'height': self.original_height
            },
            'thumbnail': {
              'url': self.thumbnail.url,
              'type': 'thumbnail',
              'width': self.thumbnail_width,
              'height': self.thumbnail_height              
            }
           }

class Entry(models.Model):

  user = models.ForeignKey(User)

  def to_json_obj(self):
    return {'id': self.id,
            'user_id': self.user.id,
            'graphUri': str(USER_GRAPH_URI).format(userId=self.id)}

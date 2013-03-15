
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from storages.backends.s3boto import S3BotoStorage

class UserProfile(models.Model):
  user = models.OneToOneField(User, primary_key=True)

  schema = models.TextField(max_length=128, null=True)


class Image(models.Model):

  user = models.ForeignKey(User)

  image = models.ImageField(upload_to='users', storage=S3BotoStorage(bucket='images.catalogit.howardburrows.com'))
  #image = models.ImageField(upload_to='users')

  def to_json_obj(self):
    return {'id': self.id,
            'user_id': self.user.id,
            'name': self.image.name,
            'url': self.image.url}
  
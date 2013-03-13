'''
Created on Oct 19, 2012

@author: howard
'''

from django.conf import settings

from piston.handler import AnonymousBaseHandler


class StatusHandler(AnonymousBaseHandler):

  allowed_methods = ('GET')

  def read(self, request):
    return {'status': 'OK',
            'authenticated': request.user.is_authenticated(),
            'STATIC_ROOT': settings.STATIC_ROOT,
            'STATIC_URL': settings.STATIC_URL,
            'STATICFILES_DIRS': settings.STATICFILES_DIRS}

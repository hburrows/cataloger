from django.conf.urls import patterns, url

from lib.cors_resource import CORSResource
from lib.django_auth import DjangoAuthentication

from handlers.status import StatusHandler
from handlers.login import LoginHandler, LogoutHandler
from handlers.users import UsersHandler
from handlers.classes import ClassesHandler
from handlers.properties import PropertiesHandler

from handlers import (
  userentry,
  images
)

'''
from handlers.useractivity import UserActivityHandler
from handlers.userentry import UserEntryHandler
from handlers.userimages import UserImageHandler
from handlers.userservice import UserServiceHandler
'''

auth = DjangoAuthentication()
ad = {'authentication': auth}

status_handler = CORSResource(StatusHandler)
login_handler = CORSResource(LoginHandler)
logout_handler = CORSResource(LogoutHandler)
users_handler = CORSResource(UsersHandler)
classes_handler = CORSResource(ClassesHandler)
properties_handler = CORSResource(PropertiesHandler)
user_entry_handler = CORSResource(userentry.UserEntryHandler, **ad)

user_image_handler = CORSResource(images.UserImagesHandler, **ad)

'''
user_service_handler = CORSResource(UserServiceHandler, **ad)
user_activity_handler = CORSResource(UserActivityHandler, **ad)
'''

# status view handler
urlpatterns = patterns('api.handlers.status',
  url(r'^status/$', status_handler, { 'emitter_format': 'json' }),
)
              
# status view handler
urlpatterns += patterns('',
  url(r'^login$', login_handler, { 'emitter_format': 'json' }),
  url(r'^logout$', logout_handler, { 'emitter_format': 'json' }),  
)
                    
# user view handlers
urlpatterns += patterns('api.views.user',

  url(r'^users/$', users_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>\d+)/$', users_handler, { 'emitter_format': 'json' }),
  url(r'^users/(?P<user_id>self)/$', users_handler, { 'emitter_format': 'json' }),

  # get list of all available classes
  url(r'^classes/$', classes_handler, { 'emitter_format': 'json' }),

  # get list of all properties for a specified class
  url(r'^classes/(?P<class_id>\S+)/$', properties_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>self|\d+)/entries/$', user_entry_handler, { 'emitter_format': 'json' }),
  url(r'^users/(?P<user_id>self|\d+)/entries/(?P<entry_id>\S+)/$', user_entry_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>self|\d+)/images/$', user_image_handler, { 'emitter_format': 'json' }),

'''
  url(r'^users/(?P<user_id>self|\d+)/services/$', user_service_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>self|\d+)/services/(?P<service_type>[a-zA-Z]+)/$', user_service_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>self|\d+)/activities/$', user_activity_handler, { 'emitter_format': 'json' }),

  url(r'^users/(?P<user_id>self|\d+)/activities/(?P<activity_id>\d+)/$', user_activity_handler, { 'emitter_format': 'json' }),


  url(r'^users/(?P<user_id>self|\d+)/entries/(?P<entry_id>\d+)/$', user_entry_handler, { 'emitter_format': 'json' }),

'''  
)

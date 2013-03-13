'''
Created on Oct 22, 2012

@author: howard
'''


from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import urlquote

from piston.utils import rc

class DjangoAuthentication(object):

  def __init__(self, login_url=None, redirect_field_name="next"):
    if not login_url:
        login_url = settings.LOGIN_URL
    self.login_url = login_url
    self.redirect_field_name = redirect_field_name
    self.request = None
  
  def is_authenticated(self, request):
    """
    `is_authenticated`: Will be called when checking for
    authentication. It returns True if the user is authenticated
    False otherwise.
    """
    self.request = request
    return request.user.is_authenticated()
      
  def challenge(self):
    return rc.FORBIDDEN
    """
    `challenge`: In cases where `is_authenticated` returns
    False, the result of this method will be returned.
    This will usually be a `HttpResponse` object with
    some kind of challenge headers and 401 code on it.
    """
    path = urlquote(self.request.get_full_path())
    tup = self.login_url, self.redirect_field_name, path 
    return HttpResponseRedirect('%s?%s=%s' %tup)

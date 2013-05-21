'''
Created on Apr 26, 2013

@author: howard
'''

from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from piston.handler import BaseHandler
from piston.utils import rc

from api.models import Graph, UserProfile

class UserGraphsHandler(BaseHandler):

  allowed_methods = ('GET', 'POST', 'DELETE')

  def read(self, request, user_id, subject_id=None):
    
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # can only view your own data unless you're a superuser
    if not request.user.is_superuser and int(user_id) != request.user.id:
      return rc.FORBIDDEN

    return [{'graph_uri': g.graph_uri, 'label': g.label} for g in request.user.userprofile.graphs.all()]
  
  def create(self, request, user_id, graph_id):
    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # create graph association
    prof = UserProfile.objects.get(user=request.user)

    try:
      g = Graph.objects.get(graph_uri=graph_id)
    except ObjectDoesNotExist:
      return rc.NOT_FOUND

    prof.graphs.add(g)
    prof.save();

    return HttpResponse({}, 'application/json; charset=utf-8', 201)

  # remove graph association
  def delete(self, request, user_id, graph_id):

    # fix-up "self" user
    if user_id.lower() == 'self':
      user_id = request.user.id

    # create profile
    prof = UserProfile.objects.get(user=request.user)
    
    try:
      g = prof.graphs.get(graph_uri=graph_id)
    except ObjectDoesNotExist:
      return rc.NOT_FOUND

    prof.graphs.remove(g)
    
    prof.save()
    
    return {}


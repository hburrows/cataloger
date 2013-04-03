from django.conf.urls import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Examples:
  # url(r'^$', 'cataloger.views.home', name='home'),
  # url(r'^cataloger/', include('cataloger.foo.urls')),

  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

  url(r'^admin/', include(admin.site.urls))
)

# static
urlpatterns += staticfiles_urlpatterns()

# app
urlpatterns += patterns('',
  url(r'^api/', include('api.urls'))
)

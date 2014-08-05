from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bole.views.home', name='home'),
    url(r'^info/', include('info.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
)

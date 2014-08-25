from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.base import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bole.views.home', name='home'),
    url(r'^info/', include('info.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r"^accounts/", include("account.urls")),
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),

    url(r'^search/', include('haystack.urls')),
)

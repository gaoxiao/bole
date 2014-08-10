# coding:utf-8
from django.conf.urls import patterns, url

from info import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='info.index'),
    url(r'^list/(\d+)$', views.list, name='info.list'),
    url(r'^by_area/(\d+)/(\d+)$', views.query_by_area, name='info.by_area'),
    url(r'^by_class/(\d+)/(\d+)$', views.query_by_class, name='info.by_class'),
    url(r'^detail/(\d+)/(.*)$', views.detail, name='info.detail')
)

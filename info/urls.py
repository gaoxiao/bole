# coding:utf-8
from django.conf.urls import patterns, url

from info import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='info.index'),
    url(r'^list/(.*)/(\d+)$', views.list, name='info.list'),
    url(r'^detail/(\d+)/(.*)$', views.detail, name='info.detail'),
    url(r'^add_fav/(\d+)/(.*)$', views.add_favourite, name='info.add_fav'),
    url(r'^rm_fav/(\d+)/(.*)$', views.rm_favourite, name='info.rm_fav'),
    url(r'^fav_list/(\d+)$', views.favourite_list, name='info.fav_list'),
    url(r'^search$', views.InfoSearchView(), name='info.search')
)

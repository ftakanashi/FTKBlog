# -*- coding:utf-8 -*-

from django.conf.urls import url

from .views import SearchView

urlpatterns = [
    url(r'^index', SearchView.as_view(), name='search_index')
]
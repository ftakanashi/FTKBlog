# -*- coding:utf-8 -*-

from django.conf.urls import url

from blog import views as BlogView
urlpatterns = [
    url(r'^$',BlogView.IndexView.as_view(), name='index')
]
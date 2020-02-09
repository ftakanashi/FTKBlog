# -*- coding:utf-8 -*-

from django.conf.urls import url

from .views import WyzCoupView, WyzCoupRepView

urlpatterns = [
   url('^$', WyzCoupView.as_view(), name='wyzcoup.coup'),
   url('^res/$', WyzCoupRepView.as_view(), name='wyzcoup.coup.receipt')
]
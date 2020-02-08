# -*- coding:utf-8 -*-

from django.conf.urls import url

from .views import WyzCoupView

urlpatterns = [
   url('^$', WyzCoupView.as_view(), name='wyzcoup.coup')
]
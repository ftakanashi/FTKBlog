# -*- coding:utf-8 -*-
from django.conf.urls import url

from .views import UserLogout, UserLogin

urlpatterns = [
    url(r'^logout/', UserLogout.as_view(),name='logout'),
    url(r'^login/', UserLogin.as_view(), name='login')
]

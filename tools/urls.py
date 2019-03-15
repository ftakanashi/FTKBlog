# -*- coding:utf-8 -*-

from django.conf.urls import url

from .views import BiologyRhythmView

urlpatterns = [
    url(r'^biology-rhythm/$', BiologyRhythmView.as_view(), name='biorhy'),
]


# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import BiologyRhythmView, PNHBDownloadView

urlpatterns = [
    url(r'^biology-rhythm/$', BiologyRhythmView.as_view(), name='biorhy'),
    url(r'^pnhb-download/$', login_required(PNHBDownloadView.as_view()), name='pnhb_download')
]


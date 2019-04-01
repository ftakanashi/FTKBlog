# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import BiologyRhythmView, PNHBDownloadView, SSRConfigView,\
    SiteDictView

urlpatterns = [
    url(r'^biology-rhythm/$', BiologyRhythmView.as_view(), name='biorhy'),
    url(r'^pnhb-download/$', login_required(PNHBDownloadView.as_view()), name='pnhb_download'),
    url(r'^ssr-config/$', SSRConfigView.as_view(), name='ssr_config'),
    url(r'^site-dict/$', SiteDictView.as_view(), name='site-dict')
]


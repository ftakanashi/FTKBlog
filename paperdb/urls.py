# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from views import IndexView, PaperView, PaperDetailView, PaperReferenceView

urlpatterns = [
    url('^index/$', IndexView.as_view(), name='paperdb.index'),
    url('^paper/$', login_required(PaperView.as_view()), name='paperdb.paper'),
    url('^paper/reference/(?P<paper_uuid>.+?)/$', PaperReferenceView.as_view(), name='paperdb.paper.reference'),
    url('^paper/detail/(?P<paper_uuid>.+?)/$', PaperDetailView.as_view(), name='paperdb.detail')
]
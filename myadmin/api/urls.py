# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from .views import CategoryListView, TagListView, PostListView, CommentListView, MessageListView, AccessControlListView, \
    PaperdbPaperListView, PaperdbCommentListView, PaperdbTagListView, PaperdbAuthorListView, WyzCoupListView

urlpatterns = [
    url(r'^category/',CategoryListView.as_view(), name='category.api'),
    url(r'^tag/', TagListView.as_view(), name='tag.api'),
    url(r'^post/', PostListView.as_view(), name='post.api'),
    url(r'^comment/',CommentListView.as_view(),name='comment.api'),
    url(r'^message/',MessageListView.as_view(),name='message.api'),
    url(r'^accesscontrol', AccessControlListView.as_view(), name='accesscontrol.api'),
    url(r'^paperdb/paper/$', PaperdbPaperListView.as_view(), name='paperdb.paper.api'),
    url(r'^paperdb/comment/$', PaperdbCommentListView.as_view(), name='paperdb.comment.api'),
    url(r'^paperdb/tag/$', PaperdbTagListView.as_view(), name='paperdb.tag.api'),
    url(r'^paperdb/author/$', PaperdbAuthorListView.as_view(), name='paperdb.author.api'),
    url(r'^wyzcoup/coup/$', WyzCoupListView.as_view(), name='wyzcoup.coup.api')
]
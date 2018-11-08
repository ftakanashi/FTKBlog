# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from .views import CategoryListView, TagListView, PostListView, CommentListView, MessageListView

urlpatterns = [
    url(r'^category/',CategoryListView.as_view(), name='category.api'),
    url(r'^tag/', TagListView.as_view(), name='tag.api'),
    url(r'^post/', PostListView.as_view(), name='post.api'),
    url(r'^comment/',CommentListView.as_view(),name='comment.api'),
    url(r'^message/',MessageListView.as_view(),name='message.api')
]
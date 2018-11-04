# -*- coding:utf-8 -*-

from django.conf.urls import url

from blog import views as BlogView
urlpatterns = [
    url(r'^$',BlogView.IndexView.as_view(), name='index'),
    url(r'^new/$',BlogView.NewPostView.as_view(), name='new_post'),
    url(r'^comment/$', BlogView.CommentView.as_view(),name='comment'),
    url(r'^(?P<uuid>.+?)/$', BlogView.PostView.as_view(), name='detail')
]
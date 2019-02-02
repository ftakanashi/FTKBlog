# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from blog import views as BlogView
urlpatterns = [
    url(r'^$',BlogView.IndexView.as_view(), name='index'),
    url(r'^new/$',login_required(BlogView.NewPostView.as_view()), name='new_post'),
    url(r'^new/upload/$',login_required(BlogView.editormd_upload), name='editormd-upload'),
    url(r'^comment/$', BlogView.CommentView.as_view(),name='comment'),
    url(r'^message/$', BlogView.MessageView.as_view(), name='message'),
    url(r'^vericode/$', BlogView.VeriCodeView.as_view(), name='veri-code'),
    url(r'^postmeta/$', BlogView.PostMetaView.as_view(), name='post_meta'),
    url(r'^(?P<uuid>.+?)/$', BlogView.PostView.as_view(), name='detail')
]
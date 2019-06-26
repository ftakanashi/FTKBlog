# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.conf.urls import url,include

from .views import *

urlpatterns = [
    url(r'^api/', include('myadmin.api.urls')),
    url(r'^$', login_required(IndexView.as_view()) ,name='my_admin_index'),
    url(r'^category', login_required(CategoryManage.as_view()), name='category.manage'),
    url(r'^tag', login_required(TagManage.as_view()),name='tag.manage'),
    url(r'^dict/', login_required(DictManage.as_view()), name='dict.manage'),
    url(r'^post/', login_required(PostManange.as_view()), name='post.manage'),
    # url(r'^post/upload/$', editormd_upload, name='edit-editormd-upload'),
    url(r'^comment/', login_required(CommentManage.as_view()), name='comment.manage'),
    url(r'^message/', login_required(MessageManage.as_view()), name='message.manage'),
    url(r'^accesscontrol/', login_required(AccessControlManage.as_view()), name='accesscontrol.manage'),
    url(r'^backupdownload/$', login_required(BackupDownloadManage.as_view()), name='backupdownload.manage'),
    url(r'^backupdownload/(?P<fn>.+?)/', login_required(backup_download), name='backupdownload.download'),
    url(r'^paperdb/paper/$', login_required(PaperdbPaperManage.as_view()), name='paperdb.manage'),
    url(r'^paperdb/tag/$', login_required(PaperdbTagManage.as_view()), name='paperdb.tag.manage'),
    url(r'^paperdb/author/$', login_required(PaperdbAuthorManage.as_view()), name='paperdb.author.manage')
]
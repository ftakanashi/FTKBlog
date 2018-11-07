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
    url(r'^comment/', login_required(CommentManage.as_view()), name='comment.manage')
]
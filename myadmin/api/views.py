# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from ratelimit.mixins import RatelimitMixin

from blog.models import Category, Tag, Post, Comment, Message
from ftkuser.models import AccessControl
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer, MessageSerializer,\
    AccessControlSerializer
from .filters import CategoryFilter, TagFilter, PostFilter, CommentFilter, MessageFilter, AccessControlFilter

class RateLimitedListView(RatelimitMixin):
    ratelimit_key = 'ip'
    ratelimit_rate = '1/s'
    ratelimit_block = True
    ratelimit_method = ['GET','POST','PUT','DELETE','PATCH']

class CategoryListView(RateLimitedListView,generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CategoryFilter

class TagListView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = TagFilter

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-edit_time')
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = PostFilter

class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all().order_by('in_post__post_id')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentFilter

class MessageListView(generics.ListCreateAPIView):
    queryset = Message.objects.all().order_by('-create_time')
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = MessageFilter

class AccessControlListView(generics.ListCreateAPIView):
    queryset = AccessControl.objects.all().order_by('source_ip')
    serializer_class = AccessControlSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = AccessControlFilter
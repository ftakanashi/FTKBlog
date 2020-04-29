# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from ratelimit.mixins import RatelimitMixin

from blog.models import Category, Tag, Post, Comment, Message
from paperdb.models import Paper, PaperComment, ResearchTag, Author
from ftkuser.models import AccessControl
from wyzcoup.models import WyzCoup
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer, MessageSerializer,\
    AccessControlSerializer, PaperdbPaperSerializer, PaperdbCommentSerializer,  PaperdbTagSerializer, PaperdbAuthorSerializer,\
    WyzCoupSerializer
from .filters import CategoryFilter, TagFilter, PostFilter, CommentFilter, MessageFilter, AccessControlFilter, \
    PaperdbTagFilter, WyzCoupFilter

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

class PaperdbPaperListView(generics.ListCreateAPIView):
    queryset = Paper.objects.all().order_by('publish_time', 'title')
    serializer_class = PaperdbPaperSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

class PaperdbCommentListView(generics.ListCreateAPIView):
    queryset = PaperComment.objects.all().order_by('-update_time')
    serializer_class = PaperdbCommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, )

class PaperdbTagListView(generics.ListCreateAPIView):
    queryset = ResearchTag.objects.all()
    serializer_class = PaperdbTagSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = PaperdbTagFilter

class PaperdbAuthorListView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = PaperdbAuthorSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )

class WyzCoupListView(generics.ListCreateAPIView):
    queryset = WyzCoup.objects.all().order_by('-create_time')
    serializer_class = WyzCoupSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = WyzCoupFilter
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from blog.models import Category, Tag, Post, Comment
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer
from .filters import CategoryFilter, TagFilter, PostFilter, CommentFilter



class CategoryListView(generics.ListCreateAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = DjangoFilterBackend,
    filter_class = CategoryFilter

class TagListView(generics.ListCreateAPIView):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = DjangoFilterBackend,
    filter_class = TagFilter

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = DjangoFilterBackend,
    filter_class = PostFilter
    ordering = ('-update_time')

class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    filter_backends = DjangoFilterBackend,
    filter_class = CommentFilter
    ordering = ('in_post__post_id')
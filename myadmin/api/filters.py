# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django_filters import FilterSet

from blog.models import Category, Tag, Post, Comment, Message


class CategoryFilter(FilterSet):
    class Meta:
        model = Category
        fields = {
            'cate_id': ['exact'],
            'name': ['contains'],
            'description': ['contains'],
            'create_time': ['gt','lt','exact'],
            'update_time': ['gt','lt','exact']
        }

class TagFilter(FilterSet):
    class Meta:
        model = Tag
        fields = {
            'tag_id': ['exact'],
            'name': ['contains'],
            'description': ['contains']
        }

class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'post_id': ['exact'],
            'post_uuid': ['exact'],
            'title': ['exact','contains'],
            'create_time': ['lt','gt'],
            'update_time': ['lt','gt'],
            'status': ['exact'],
            'is_reprint': ['exact'],
            'is_top': ['exact']
        }

class CommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = {
            'comment_id': ['exact'],
            'create_time': ['lt','gt'],
            'in_post__post_id': ['exact'],
            'in_post__post_uuid': ['exact'],
            'author': ['contains'],
            'content': ['contains'],
            'email': ['contains'],
            'floor': ['exact'],
            'source_ip': ['exact']
        }

class MessageFilter(FilterSet):
    class Meta:
        model = Message
        fields = {
            'message_id': ['exact'],
            'create_time': ['lt','gt'],
            'relate_post__post_id': ['exact'],
            'relate_post__post_uuid': ['exact'],
            'author': ['contains'],
            'content': ['contains'],
            'contact': ['contains'],
            'source_ip': ['exact']
        }
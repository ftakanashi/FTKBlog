# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SlugRelatedField,StringRelatedField

from blog.models import Category, Tag, Post, Comment, Message
from ftkuser.models import AccessControl

class CategorySerializer(ModelSerializer):
    in_category_posts = SlugRelatedField(slug_field='post_uuid', read_only=True, many=True)
    # in_category_posts = StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(ModelSerializer):
    in_tag_posts = SlugRelatedField(slug_field='title', read_only=True, many=True)

    class Meta:
        model = Tag
        fields = '__all__'

class PostSerializer(ModelSerializer):
    category = SlugRelatedField(slug_field='name', read_only=True)
    tag = SlugRelatedField(slug_field='name', many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('post_id','post_uuid','title','create_time',
                  'update_time','edit_time','status','is_reprint','is_top',
                  'read_count','greats','category','tag')

class CommentSerializer(ModelSerializer):

    in_post = SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    relate_post = SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

class AccessControlSerializer(ModelSerializer):

    class Meta:
        model = AccessControl
        fields = '__all__'
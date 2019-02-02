# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import uuid


# Create your models here.

class Category(models.Model):
    cate_id = models.AutoField(primary_key=True, verbose_name='分类ID')
    name = models.CharField(max_length=64, verbose_name='分类名称', unique=True)
    description = models.CharField(max_length=512, verbose_name='分类描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __unicode__(self):
        return '%s: <Category %s>' % (self.cate_id, self.name)


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512)

    def __unicode__(self):
        return '%s: <Tag %s>' % (self.tag_id, self.name)


class Post(models.Model):
    POST_STATUS = [('0', '发布'), ('1', '草稿')]

    post_id = models.AutoField(primary_key=True, verbose_name='文章真实ID')
    post_uuid = models.UUIDField(default=uuid.uuid4, verbose_name='文章伪装ID')
    title = models.CharField(max_length=256, verbose_name='文章标题', unique=True)
    abstract = models.CharField(max_length=256, verbose_name='文章摘要')
    content = models.TextField(null=True, default='', verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='自动更新时间')
    edit_time = models.DateTimeField(auto_now_add=True, verbose_name='编辑更新时间')
    status = models.CharField(default='0', max_length=1, choices=POST_STATUS, verbose_name='文章状态')
    read_count = models.IntegerField(default=0,verbose_name='浏览量')
    greats = models.IntegerField(default=0, verbose_name='点赞量')
    category = models.ForeignKey(
            Category,
            null=True,
            on_delete=models.SET_NULL,
            related_name='in_category_posts',
            verbose_name='文章分类'
    )
    tag = models.ManyToManyField(
            Tag,
            blank=True,
            null=True,
            related_name='in_tag_posts',
            verbose_name='文章标签'
    )

    is_reprint = models.BooleanField(default=False, verbose_name='转载')
    reprint_src = models.CharField(max_length=512, blank=True, null=True, verbose_name='转载源')
    is_top = models.BooleanField(default=False, verbose_name='置顶')

    def __unicode__(self):
        if self.category is not None:
            return '[%s] <%s: %s>' % (self.post_id, self.category.name, self.title)
        else:
            return '[%s] <NoCategory: %s>' % (self.post_id, self.title)

# class PostImage(models.Model):
#     image = models.ImageField(upload_to='upload',verbose_name='图片')
#     title = models.CharField(max_length=64,verbose_name='图片标题')
#     in_post = models.ForeignKey(
#         Post,
#         on_delete=models.CASCADE,
#         related_name='post_images',
#         verbose_name='所属文章'
#     )

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True,verbose_name='评论ID')
    comment_uuid = models.UUIDField(default=uuid.uuid4,verbose_name='评论UUID')
    source_ip = models.GenericIPAddressField(default='',null=True,verbose_name='留言者IP')
    in_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属文章'
    )
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='评论时间')
    author = models.TextField(max_length=128,verbose_name='评论者')
    title = models.TextField(max_length=256,default='无题',verbose_name='评论标题')
    content = models.TextField(max_length=2048,verbose_name='评论内容')
    email = models.EmailField(null=True,blank=True,verbose_name='邮箱地址')
    floor = models.IntegerField(default=1,verbose_name='楼层')
    reply_to = models.CharField(max_length=32,default='',verbose_name='回复楼层')

    def __unicode__(self):
        return '%s: <Comment %s>' % (self.comment_id,self.author)


class PostMeta(models.Model):
    post_meta_id = models.AutoField(primary_key=True, verbose_name='文章metaID')
    title = models.TextField(max_length=128, default='', verbose_name='meta标题')
    content = models.TextField(max_length=2048, default='', verbose_name='meta内容')
    in_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='metas',
        verbose_name='所属文章'
    )

    def __unicode__(self):
        return '{}: <PostMeta {}>'.format(self.post_meta_id, self.title)

class Dict(models.Model):
    key = models.CharField(max_length=128,primary_key=True,verbose_name='数据字典键')
    value = models.CharField(max_length=1024,verbose_name='数据字典值')
    category = models.CharField(max_length=16, default='default', verbose_name='项分类')
    comment = models.CharField(max_length=256, default='', verbose_name='备注')

    def __unicode__(self):
        return '<DictItem>%s:%s' % (self.key,self.value)

class Message(models.Model):
    message_id = models.AutoField(primary_key=True,verbose_name='留言ID')
    author = models.CharField(max_length=64, verbose_name='作者昵称')
    source_ip = models.GenericIPAddressField(verbose_name='来源IP')
    contact = models.CharField(max_length=128, null=True, verbose_name='联系方式')
    title = models.CharField(max_length=128,default='无题',verbose_name='标题')
    content = models.TextField(max_length=1024,verbose_name='内容')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    relate_post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        related_name='relate_messages',
        verbose_name='关联文章'
    )

    def __unicode__(self):
        return '%s: <Message>%s via %s' % (self.message_id, self.title,self.author)



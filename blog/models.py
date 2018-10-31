# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import uuid


# Create your models here.

class Category(models.Model):
    cate_id = models.AutoField(primary_key=True, verbose_name='分类ID')
    name = models.CharField(max_length=64, verbose_name='分类名称')
    description = models.CharField(max_length=512, verbose_name='分类描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __unicode__(self):
        return '%s: <Category %s>' % (self.cate_id, self.name)


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=512)

    def __unicode__(self):
        return '%s: <Tag %s>' % (self.tag_id, self.name)


class Post(models.Model):
    POST_STATUS = [('0', '发布'), ('1', '草稿')]

    post_id = models.AutoField(primary_key=True, verbose_name='文章真实ID')
    post_uuid = models.UUIDField(default=uuid.uuid1, verbose_name='文章伪装ID')
    title = models.CharField(max_length=256, verbose_name='文章标题', unique=True)
    abstract = models.CharField(max_length=256, verbose_name='文章摘要')
    content = models.TextField(null=True, default='', verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.CharField(default='0', max_length=1, choices=POST_STATUS, verbose_name='文章状态')
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

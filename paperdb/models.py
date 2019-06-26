# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models


# Create your models here.

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False)

    def __unicode__(self):
        return '<Author {}>{}'.format(self.author_id, self.name)

    class Meta:
        unique_together = ('name', )


class ResearchTag(models.Model):
    research_tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, null=False, unique=True)
    description = models.CharField(max_length=512, null=True, default='')

    def __unicode__(self):
        return '<Research Tag {}>{}'.format(self.research_tag_id, self.name)


class PaperComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    content = models.TextField(default='', verbose_name='评论内容')

    def __unicode__(self):
        return '<Paper Comment {}>{}'.format(self.comment_id, self.content)


class Paper(models.Model):
    paper_uuid = models.UUIDField(default=uuid.uuid4, verbose_name='论文UUID', primary_key=True)
    title = models.CharField(max_length=256, verbose_name='论文标题', unique=True)
    publish_time = models.DateField(verbose_name='发表时间')
    publish_origin = models.CharField(max_length=128, default='unknown', verbose_name='发表刊物/会议')
    self_score = models.IntegerField(default=-1, verbose_name='打分')
    link = models.URLField(null=True, verbose_name='论文链接')
    author = models.ManyToManyField(
            Author,
            blank=False,
            related_name='papers',
            verbose_name='作者'
    )
    tag = models.ManyToManyField(
            ResearchTag,
            blank=True,
            related_name='papers',
            verbose_name='研究方向标签'
    )
    comment = models.OneToOneField(
            PaperComment,
            null=True,
            blank=True,
            default=None,
            on_delete=models.SET_NULL,
            related_name='paper',
            verbose_name='评论'
    )

    def __unicode__(self):
        return '<Paper {}>{}'.format(self.paper_uuid, self.title)

    def get_reference_by_time(self):
        for refer in sorted(self.reference.all(), key=lambda x: x.reference_trg.publish_time.year):
            yield refer.reference_trg

    def get_apa_format(self):
        return '{}. ({}). {} {}'.format(
            '. '.join([a.name for a in self.author.all()]),
            self.publish_time.year,
            self.title,
            self.publish_origin
        )

class Reference(models.Model):

    reference_id = models.AutoField(primary_key=True)
    reference_src = models.ForeignKey(
        Paper,
        null=False,
        verbose_name='引用源',
        related_name='reference'
    )
    reference_trg = models.ForeignKey(
        Paper,
        null=False,
        verbose_name='被引用源',
        related_name='be_referred'
    )

    def __unicode__(self):
        return '<Reference {}>[{} -> {}]'\
            .format(self.reference_id, self.reference_src.title, self.reference_trg.title)

    class Meta:
        unique_together = ('reference_src', 'reference_trg')
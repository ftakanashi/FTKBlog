# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models

COUP_STATUS = [
    ('0', '未使用'),
    ('1', '已使用'),
    ('2', '已过期')
]

# Create your models here.
class WyzCoup(models.Model):
    coup_uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name='UUID')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    coup_status = models.CharField(null=False, default='0', max_length=1, choices=COUP_STATUS, verbose_name='好人卡状态')
    consume_time = models.DateTimeField(null=True, default=None, verbose_name='使用时间')
    expire_time = models.DateTimeField(null=True, default=None, verbose_name='过期时间')    # None表示无限期
    coup_title = models.CharField(null=False, max_length=128, verbose_name='好人卡标题')
    coup_content = models.CharField(default='', max_length=1024, verbose_name='好人卡内容')
    coup_note = models.CharField(default='', max_length=2048, verbose_name='好人卡使用备注')

    def __unicode__(self):
        return '<CoupForMySweet {}>{}'.format(self.coup_uuid, self.coup_title)
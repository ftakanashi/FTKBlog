# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.

class Slogan(models.Model):

    slogan_id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=1024)
    author = models.TextField(max_length=128)

class AccessControl(models.Model):

    CONTROL_TYPE = [('0','白名单'),('1','黑名单')]

    ac_id = models.AutoField(primary_key=True)
    source_ip = models.GenericIPAddressField()
    control_type = models.CharField(max_length=2, choices=CONTROL_TYPE)
    domain = models.CharField(max_length=32,default='root')

    class Meta:
        unique_together = ('source_ip','control_type', 'domain')

    def __unicode__(self):
        if self.control_type == '0':
            return '<WhiteList @%s> %s' % (self.domain, self.source_ip)
        elif self.control_type == '1':
            return '<BlackList @%s> %s' % (self.domain, self.source_ip)
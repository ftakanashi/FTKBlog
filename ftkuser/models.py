# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.

class Slogan(models.Model):

    slogan_id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=1024)
    author = models.TextField(max_length=128)
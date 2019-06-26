# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import Paper, Author, ResearchTag, PaperComment
# Register your models here.
admin.site.register([
    Author,
    ResearchTag,
    PaperComment,
    Paper
])


# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.conf import settings
from django_redis import get_redis_connection

from blog.models import Post

DATEFMT = '%Y-%m-%d %H:%M:%S'

def sync_read_count():
    print '[%s]Start to sync read_count from redis to db...' % datetime.datetime.now().strftime(DATEFMT)
    try:
        r = get_redis_connection('default')
        for post in Post.objects.all():
            rc = r.hget(settings.READ_COUNT_KEY, post.post_uuid) or 0
            post.read_count = rc
            post.save()
    except Exception,e:
        print '[%s]Failed to sync.' % datetime.datetime.now().strftime(DATEFMT)
        raise

def refresh_today_access_count():
    r = get_redis_connection('default')
    r.set(settings.ACCESS_COUNT_KEY,0)
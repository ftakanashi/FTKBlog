# -*- coding:utf-8 -*-

from redis import Redis
from django.conf import settings

def init():
    redis_info = settings.CACHES.DEFAULT.LOCATION
    try:
        r = Redis(redis_info)
    except Exception,e:
        print 'Failed to connect into Redis'
        raise
    r.hset('read_count','_','_')
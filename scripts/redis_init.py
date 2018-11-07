# -*- coding:utf-8 -*-

import re

from redis import Redis
from django.conf import settings

def redis_init():
    redis_info = settings.CACHES.get('default')
    m = re.match('redis\:\/\/(.+?)\:(\d+?)\/(\d+)$',redis_info.get('LOCATION'))
    host,port,db = m.group(1),m.group(2),m.group(3)
    password = redis_info.get('OPTIONS').get('PASSWORD')
    try:
        r = Redis(host=host,port=port,db=db,password=password)
    except Exception,e:
        print 'Failed to connect into Redis'
        raise

    if not r.exists(settings.READ_COUNT_KEY):
        r.hset(settings.READ_COUNT_KEY,'_',0)
        r.hdel(settings.READ_COUNT_KEY,'_')

    if not r.exists(settings.ACCESS_COUNT_KEY):
        r.set(settings.ACCESS_COUNT_KEY,0)

    if not r.exists(settings.UNREAD_COMMENTS_KEY):
        r.rpush(settings.UNREAD_COMMENTS_KEY,'1')
        # r.lpop(settings.UNREAD_COMMENTS_KEY)

    for key in (settings.READ_COUNT_KEY,settings.ACCESS_COUNT_KEY, settings.UNREAD_COMMENTS_KEY):
        r.persist(key)

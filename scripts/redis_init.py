# -*- coding:utf-8 -*-

import re

from redis import Redis
from django.conf import settings

def redis_init():
    '''
    这里定义的操作会在每次应用启动时被执行。
    '''
    redis_info = settings.CACHES.get('default')
    m = re.match('redis\:\/\/(.+?)\:(\d+?)\/(\d+)$',redis_info.get('LOCATION'))
    host,port,db = m.group(1),m.group(2),m.group(3)
    password = redis_info.get('OPTIONS').get('PASSWORD')
    try:
        r = Redis(host=host,port=port,db=db,password=password)
    except Exception,e:
        print 'Failed to connect into Redis'
        raise

    if not r.exists(settings.SITE_MEMO_KEY):
        r.hset(settings.SITE_MEMO_KEY, -1, '')

    if not r.exists(settings.READ_COUNT_KEY):
        r.hset(settings.READ_COUNT_KEY,'_',0)

    if not r.exists(settings.ACCESS_COUNT_KEY):
        r.set(settings.ACCESS_COUNT_KEY,0)

    if not r.exists(settings.UNREAD_COMMENTS_KEY):
        r.rpush(settings.UNREAD_COMMENTS_KEY,'-1')

    if not r.exists(settings.UNREAD_MESSAGE_KEY):
        r.rpush(settings.UNREAD_MESSAGE_KEY, '-1')

    if not r.exists(settings.ACCESS_IP_QUEUE):
        r.rpush(settings.ACCESS_IP_QUEUE, '127.0.0.1|1970-01-01 00:00:00|1')

    for key in (
        settings.SITE_MEMO_KEY,
        settings.READ_COUNT_KEY,
        settings.ACCESS_COUNT_KEY,
        settings.UNREAD_COMMENTS_KEY,
        settings.UNREAD_MESSAGE_KEY
    ):
        r.persist(key)

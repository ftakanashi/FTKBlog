# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime
import os
import shutil

from django.conf import settings
from django_redis import get_redis_connection

from blog.models import Post
# todo 搞一个logger规范cron日志输出格式
DATEFMT = '%Y-%m-%d %H:%M:%S'

def sync_read_count():
    '''
    定期将redis中的数据同步到数据库中
    :return:
    '''
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
    '''
    每天零点归零当天来访访客数
    :return:
    '''
    r = get_redis_connection('default')
    r.set(settings.ACCESS_COUNT_KEY,0)

def gc_post_images():
    '''
    定期检查post-image上传目录中是否有无效的文章uuid情况，若有则直接删除之
    :return:
    '''
    for _post_uuid in os.listdir(settings.IMG_UPLOAD_DIR):
        try:
            post = Post.objects.get(post_uuid=_post_uuid)
        except Post.DoesNotExist,e:
            shutil.rmtree(os.path.join(settings.IMG_UPLOAD_DIR, _post_uuid))
        else:
            continue
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import logging
import os
import shutil

from django.conf import settings
from django_redis import get_redis_connection

from blog.models import Post
DATEFMT = '%Y-%m-%d %H:%M:%S'
CRONLOG = os.path.join(settings.PROJECT_ROOT, 'logs', 'cron', 'cron.log')

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(filename)s [L.%(lineno)d] %(levelname)s  %(message)s',
                    datefmt=DATEFMT, filename=CRONLOG)

def sync_read_count():
    '''
    定期将redis中的数据同步到数据库中
    :return:
    '''
    logging.info('Start to sync read_count from redis to db...')
    try:
        r = get_redis_connection('default')
        for post in Post.objects.all():
            rc = r.hget(settings.READ_COUNT_KEY, post.post_uuid) or 0
            post.read_count = rc
            post.save()
    except Exception,e:
        logging.error('Failed to sync: %s' % unicode(e))
        raise
    else:
        logging.info('read_count sync over.')

def refresh_today_access_count():
    '''
    每天零点归零当天来访访客数
    :return:
    '''
    logging.info('Reset access count to 0...')
    try:
        r = get_redis_connection('default')
        r.set(settings.ACCESS_COUNT_KEY,0)
    except Exception,e:
        logging.error('Failed to reset access count: %s' % unicode(e))
    else:
        logging.info('reset over')

def gc_post_images():
    '''
    定期检查post-image上传目录中是否有无效的文章uuid情况，若有则直接删除之
    :return:
    '''
    logging.info('Start to check invalid post-images..')
    deleted_count = 0
    for _post_uuid in os.listdir(settings.IMG_UPLOAD_DIR):
        try:
            post = Post.objects.get(post_uuid=_post_uuid)
        except Post.DoesNotExist,e:
            logging.info('Deleting directory: %s' % os.path.join(_post_uuid))
            shutil.rmtree(os.path.join(settings.IMG_UPLOAD_DIR, _post_uuid))
            deleted_count += 1
        else:
            continue

    logging.info('Deleted %s directories' % deleted_count)
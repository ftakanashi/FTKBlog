# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import logging
import os
import traceback

from django.conf import settings
from django_redis import get_redis_connection
from subprocess import Popen, PIPE

from utils import RateQuery

logger = logging.getLogger('django.ftkblog.cron')

redis = get_redis_connection()

def upload_to_baidu():
    '''
    同步上传百度云，节省本机空间
    :return:
    '''
    cmd = 'ps -ef | grep -E \'/usr/local/bin/you-get|bypy\' | grep -v grep | wc -l'
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out,err = p.communicate()
    if int(out) > 0:
        logger.warning('发现有you-get下载中或bypy上传中的任务，放弃同步')
        return

    base = settings.TOOLS_CONFIG['you-get']['default_download_path']
    file_pool = os.listdir(base)
    processes = []
    for f in file_pool:
        cmd = 'bypy upload \'{0}\' /you-get'.format(os.path.join(base, f))
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        p.file_name = f
        processes.append(p)
        logger.info('文件[{}]已经开始上传'.format(f))

    for p in processes:
        out,err = p.communicate()
        if err:
            logger.error(err)
        else:
            logger.info('文件{}上传完成'.format(p.file_name))

    for f in file_pool:
        cmd = 'rm -f \'{}\''.format(os.path.join(base, f))
        flag = os.system(cmd)
        if flag != 0:
            logger.warning('删除文件{}失败'.format(f))


def auto_rate_update():
    '''
    自动获取最新汇率信息
    :return:
    '''
    cache_key = settings.TOOLS_CONFIG['rate_tool']['redis_key']
    root_url = settings.TOOLS_CONFIG['rate_tool']['root_url']
    try:
        rate_query = RateQuery(root_url)
        info = rate_query.query()
        if len(info) == 0:
            logger.info('没有找到汇率信息')
            return
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {'data': info, 'update_time': update_time}
        redis.set(cache_key, json.dumps(data))
    except Exception as e:
        logger.error('获取汇率信息失败:\n{}'.format(traceback.format_exc(e)))
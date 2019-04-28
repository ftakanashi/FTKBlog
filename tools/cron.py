# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import logging
import os

from django.conf import settings
from subprocess import Popen, PIPE

logger = logging.getLogger('django.ftkblog.cron')

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

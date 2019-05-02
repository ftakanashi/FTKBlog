# -*- coding:utf-8 -*-

import os

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def you_get(**kwargs):
    url = kwargs.get('url')
    with_caption = kwargs.get('with_caption')
    form = kwargs.get('form')
    default_path = kwargs.get('default_path')
    output_fn = kwargs.get('output_fn')
    list_download = kwargs.get('list_download')

    cmd = 'you-get'
    if list_download:
        cmd += ' --playlist'
    else:
        if output_fn is not None and output_fn != '':
            cmd += ' -O {}'.format(output_fn)

    cmd += ' --format={} -o {}'.format(form, default_path)

    if not with_caption:
        cmd += ' --no-caption'

    cmd += ' {}'.format(url)

    logger.info('you-get 命令:[{}]'.format(cmd))
    return os.system(cmd)
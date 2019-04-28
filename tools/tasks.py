# -*- coding:utf-8 -*-

import os

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def you_get(**kwargs):
    url = kwargs.get('url')
    form = kwargs.get('form')
    with_caption = kwargs.get('with_caption')
    default_path = kwargs.get('default_path')
    output_fn = kwargs.get('output_fn')
    cmd = 'you-get --format={} -o {}'.format(form, default_path)

    if not with_caption:
        cmd += ' --no-caption'

    if output_fn != '':
        cmd += ' -O {}'.format(output_fn)

    cmd += ' {}'.format(url)

    logger.info('you-get 命令:[{}]'.format(cmd))
    return os.system(cmd)
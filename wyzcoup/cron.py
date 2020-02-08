# -*- coding:utf-8 -*-

import datetime

from wyzcoup.models import WyzCoup

def expire_coups():
    for coup in WyzCoup.objects.filter(coup_status='0'):
        if coup.expire_time is not None and coup.expire_time < datetime.datetime.now():
            coup.coup_status = '2'
            coup.save()
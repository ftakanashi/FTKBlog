# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-26 06:03
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='edit_time',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 11, 26, 14, 3, 59, 921705), verbose_name='\u7f16\u8f91\u66f4\u65b0\u65f6\u95f4'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u81ea\u52a8\u66f4\u65b0\u65f6\u95f4'),
        ),
    ]

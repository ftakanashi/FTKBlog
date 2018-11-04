# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-04 00:01
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20181102_1724'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-create_time',)},
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_uuid',
            field=models.UUIDField(default=uuid.uuid4, verbose_name='\u8bc4\u8bbaUUID'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='\u8bc4\u8bbaID'),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_uuid',
            field=models.UUIDField(default=uuid.uuid4, verbose_name='\u6587\u7ae0\u4f2a\u88c5ID'),
        ),
    ]

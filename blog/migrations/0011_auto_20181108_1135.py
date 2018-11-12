# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-08 03:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_comment_source_ip'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.AutoField(primary_key=True, serialize=False, verbose_name='\u7559\u8a00ID')),
                ('author', models.CharField(max_length=64, verbose_name='\u4f5c\u8005\u6635\u79f0')),
                ('source_ip', models.GenericIPAddressField(verbose_name='\u6765\u6e90IP')),
                ('contact', models.CharField(max_length=128, verbose_name='\u8054\u7cfb\u65b9\u5f0f')),
                ('title', models.CharField(max_length=128, verbose_name='\u6807\u9898')),
                ('content', models.TextField(max_length=1024, verbose_name='\u5185\u5bb9')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('relate_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='relate_messages', to='blog.Post', verbose_name='\u5173\u8054\u6587\u7ae0')),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='source_ip',
            field=models.GenericIPAddressField(default='', null=True, verbose_name='\u7559\u8a00\u8005IP'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-20 04:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('cate_id', models.AutoField(primary_key=True, serialize=False, verbose_name='\u5206\u7c7bID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='\u5206\u7c7b\u540d\u79f0')),
                ('description', models.CharField(max_length=512, verbose_name='\u5206\u7c7b\u63cf\u8ff0')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False, verbose_name='\u8bc4\u8bbaID')),
                ('comment_uuid', models.UUIDField(default=uuid.uuid4, verbose_name='\u8bc4\u8bbaUUID')),
                ('source_ip', models.GenericIPAddressField(default='', null=True, verbose_name='\u7559\u8a00\u8005IP')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u8bc4\u8bba\u65f6\u95f4')),
                ('author', models.TextField(max_length=128, verbose_name='\u8bc4\u8bba\u8005')),
                ('title', models.TextField(default='\u65e0\u9898', max_length=256, verbose_name='\u8bc4\u8bba\u6807\u9898')),
                ('content', models.TextField(max_length=2048, verbose_name='\u8bc4\u8bba\u5185\u5bb9')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='\u90ae\u7bb1\u5730\u5740')),
                ('floor', models.IntegerField(default=1, verbose_name='\u697c\u5c42')),
                ('reply_to', models.CharField(default='', max_length=32, verbose_name='\u56de\u590d\u697c\u5c42')),
            ],
        ),
        migrations.CreateModel(
            name='Dict',
            fields=[
                ('key', models.CharField(max_length=128, primary_key=True, serialize=False, verbose_name='\u6570\u636e\u5b57\u5178\u952e')),
                ('value', models.CharField(max_length=1024, verbose_name='\u6570\u636e\u5b57\u5178\u503c')),
                ('category', models.CharField(default='default', max_length=16, verbose_name='\u9879\u5206\u7c7b')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.AutoField(primary_key=True, serialize=False, verbose_name='\u7559\u8a00ID')),
                ('author', models.CharField(max_length=64, verbose_name='\u4f5c\u8005\u6635\u79f0')),
                ('source_ip', models.GenericIPAddressField(verbose_name='\u6765\u6e90IP')),
                ('contact', models.CharField(max_length=128, null=True, verbose_name='\u8054\u7cfb\u65b9\u5f0f')),
                ('title', models.CharField(default='\u65e0\u9898', max_length=128, verbose_name='\u6807\u9898')),
                ('content', models.TextField(max_length=1024, verbose_name='\u5185\u5bb9')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_id', models.AutoField(primary_key=True, serialize=False, verbose_name='\u6587\u7ae0\u771f\u5b9eID')),
                ('post_uuid', models.UUIDField(default=uuid.uuid4, verbose_name='\u6587\u7ae0\u4f2a\u88c5ID')),
                ('title', models.CharField(max_length=256, unique=True, verbose_name='\u6587\u7ae0\u6807\u9898')),
                ('abstract', models.CharField(max_length=256, verbose_name='\u6587\u7ae0\u6458\u8981')),
                ('content', models.TextField(default='', null=True, verbose_name='\u6587\u7ae0\u5185\u5bb9')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('status', models.CharField(choices=[('0', '\u53d1\u5e03'), ('1', '\u8349\u7a3f')], default='0', max_length=1, verbose_name='\u6587\u7ae0\u72b6\u6001')),
                ('read_count', models.IntegerField(default=0, verbose_name='\u6d4f\u89c8\u91cf')),
                ('greats', models.IntegerField(default=0, verbose_name='\u70b9\u8d5e\u91cf')),
                ('is_reprint', models.BooleanField(default=False, verbose_name='\u8f6c\u8f7d')),
                ('reprint_src', models.CharField(blank=True, max_length=512, null=True, verbose_name='\u8f6c\u8f7d\u6e90')),
                ('is_top', models.BooleanField(default=False, verbose_name='\u7f6e\u9876')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='in_category_posts', to='blog.Category', verbose_name='\u6587\u7ae0\u5206\u7c7b')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tag_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('description', models.CharField(max_length=512)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, related_name='in_tag_posts', to='blog.Tag', verbose_name='\u6587\u7ae0\u6807\u7b7e'),
        ),
        migrations.AddField(
            model_name='message',
            name='relate_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='relate_messages', to='blog.Post', verbose_name='\u5173\u8054\u6587\u7ae0'),
        ),
        migrations.AddField(
            model_name='comment',
            name='in_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='blog.Post', verbose_name='\u6240\u5c5e\u6587\u7ae0'),
        ),
    ]

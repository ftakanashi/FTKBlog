# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-06-14 01:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paperdb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='comment',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='paper', to='paperdb.PaperComment', verbose_name='\u8bc4\u8bba'),
        ),
    ]

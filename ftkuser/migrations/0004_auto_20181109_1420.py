# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-09 06:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ftkuser', '0003_auto_20181109_1337'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='accesscontrol',
            unique_together=set([('source_ip', 'control_type', 'domain')]),
        ),
    ]

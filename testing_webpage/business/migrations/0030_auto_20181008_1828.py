# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-08 23:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0029_auto_20181004_0027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keyword',
            name='work_area',
        ),
        migrations.DeleteModel(
            name='KeyWord',
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-17 02:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0043_auto_20180706_0147'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessstate',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='businessstate',
            name='description_es',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
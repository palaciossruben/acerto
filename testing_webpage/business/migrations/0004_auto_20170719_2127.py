# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-19 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
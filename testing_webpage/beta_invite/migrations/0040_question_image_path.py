# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-23 03:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0039_auto_20170926_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image_path',
            field=models.CharField(max_length=200, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-27 18:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0127_campaign_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='image',
            field=models.CharField(max_length=500, null=True),
        ),
    ]

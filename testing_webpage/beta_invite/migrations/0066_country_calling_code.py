# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-04 02:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0065_auto_20171221_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='calling_code',
            field=models.IntegerField(null=True),
        ),
    ]

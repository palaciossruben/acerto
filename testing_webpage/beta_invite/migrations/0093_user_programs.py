# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-05 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0092_auto_20180404_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='programs',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
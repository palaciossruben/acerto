# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-24 00:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0114_auto_20180624_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='cut_score',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='final_score',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='passed',
            field=models.NullBooleanField(),
        ),
    ]

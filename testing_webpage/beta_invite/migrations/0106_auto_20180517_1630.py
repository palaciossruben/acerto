# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-05-17 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0105_auto_20180514_0400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bullet',
            name='name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='bullet',
            name='name_es',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='description',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='description_es',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]
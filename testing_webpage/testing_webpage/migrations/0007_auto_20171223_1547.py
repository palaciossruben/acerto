# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-23 15:47
from __future__ import unicode_literals

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('testing_webpage', '0006_auto_20171223_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendingemail',
            name='body_is_filename',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='pendingemail',
            name='override_dict',
            field=picklefield.fields.PickledObjectField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='pendingemail',
            name='with_localization',
            field=models.BooleanField(default=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-28 00:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0166_user_education_experiences'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='audio_url',
            field=models.CharField(default='#', max_length=200),
        ),
    ]

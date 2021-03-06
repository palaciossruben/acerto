# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-09 15:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0051_auto_20171102_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='interview',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Interview'),
        ),
        migrations.AddField(
            model_name='survey',
            name='video_token',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Test'),
        ),
    ]

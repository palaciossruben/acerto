# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-01 16:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0088_auto_20180319_0255'),
        ('business', '0022_auto_20180307_0051'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessuser',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.City'),
        ),
        migrations.AddField(
            model_name='businessuser',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Country'),
        ),
    ]

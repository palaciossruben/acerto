# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-15 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_state_is_rejected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='state',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.State'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-03 22:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0150_auto_20181003_1742'),
        ('business', '0026_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='work_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.WorkArea'),
        ),
    ]

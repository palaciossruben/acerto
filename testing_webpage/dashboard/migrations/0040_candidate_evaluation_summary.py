# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-24 20:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0116_auto_20180624_2028'),
        ('dashboard', '0039_businessstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='evaluation_summary',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.EvaluationSummary'),
        ),
    ]

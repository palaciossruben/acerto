# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-21 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_candidate_evaluations'),
        ('testing_webpage', '0002_auto_20171221_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailsent',
            name='candidate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Candidate'),
        ),
    ]

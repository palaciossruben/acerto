# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-22 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0035_auto_20170922_0525'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Test')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.User')),
            ],
            options={
                'db_table': 'scores',
            },
        ),
    ]

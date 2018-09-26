# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-09-26 00:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0144_workarea_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequirementBinaryQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, null=True)),
                ('name_es', models.CharField(max_length=40, null=True)),
                ('statement', models.CharField(max_length=400, null=True)),
                ('statement_es', models.CharField(max_length=400, null=True)),
            ],
            options={
                'db_table': 'requirement_binary_questions',
            },
        ),
    ]

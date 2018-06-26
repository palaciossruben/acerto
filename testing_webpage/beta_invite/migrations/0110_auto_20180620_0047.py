# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-20 00:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0109_campaign_operational_efficiency'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkAreaType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_es', models.CharField(max_length=200, null=True)),
            ],
            options={
                'db_table': 'work_areas_types',
            },
        ),
        migrations.AddField(
            model_name='workarea',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.WorkAreaType'),
        ),
    ]

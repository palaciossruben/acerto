# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-19 19:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('message', models.CharField(max_length=200, null=True)),
                ('message_es', models.CharField(max_length=200, null=True)),
            ],
            options={
                'db_table': 'plans',
            },
        ),
        migrations.AlterModelTable(
            name='user',
            table='business_users',
        ),
        migrations.AddField(
            model_name='user',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Plan'),
        ),
    ]

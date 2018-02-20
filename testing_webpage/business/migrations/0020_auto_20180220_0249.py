# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-02-20 02:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0019_auto_20180220_0247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'companies',
            },
        ),
        migrations.RemoveField(
            model_name='businessuser',
            name='company_name',
        ),
        migrations.AddField(
            model_name='businessuser',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Company'),
        ),
    ]

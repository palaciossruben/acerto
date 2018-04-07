# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-04-04 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0089_campaign_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_es', models.CharField(max_length=200, null=True)),
                ('sex', models.IntegerField()),
            ],
            options={
                'db_table': 'gender',
            },
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
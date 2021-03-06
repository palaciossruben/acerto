# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-26 16:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0013_user_is_mobile'),
        ('business', '0005_user_auth_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience', models.IntegerField()),
                ('skills', django.contrib.postgres.fields.jsonb.JSONField()),
                ('user_ids', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business.User')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Country')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Profession')),
            ],
            options={
                'db_table': 'offers',
            },
        ),
    ]

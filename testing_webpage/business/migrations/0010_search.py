# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-04 16:37
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0013_user_is_mobile'),
        ('business', '0009_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(null=True)),
                ('experience', models.IntegerField(null=True)),
                ('skills', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('user_ids', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Country')),
                ('education', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Education')),
                ('profession', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Profession')),
            ],
            options={
                'db_table': 'searches',
            },
        ),
    ]

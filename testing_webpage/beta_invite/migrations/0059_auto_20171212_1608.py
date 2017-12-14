# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-12 16:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0058_auto_20171211_2103'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Campaign')),
            ],
            options={
                'db_table': 'emails_sent',
            },
        ),
        migrations.CreateModel(
            name='EmailType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('sync', models.NullBooleanField()),
            ],
            options={
                'db_table': 'email_types',
            },
        ),
        migrations.AddField(
            model_name='emailsent',
            name='email_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.EmailType'),
        ),
        migrations.AddField(
            model_name='emailsent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='beta_invite.User'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-10 02:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0024_auto_20180402_0203'),
        ('beta_invite', '0107_campaign_work_area'),
        ('testing_webpage', '0011_auto_20180610_0108'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessUserPendingEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=3)),
                ('body_input', models.CharField(max_length=10000)),
                ('subject', models.CharField(max_length=200)),
                ('with_localization', models.BooleanField(default=True)),
                ('body_is_filename', models.BooleanField(default=True)),
                ('override_dict', picklefield.fields.PickledObjectField(default={}, editable=False)),
                ('sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_users', models.ManyToManyField(to='business.BusinessUser')),
                ('email_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='beta_invite.EmailType')),
            ],
            options={
                'db_table': 'business_user_pending_emails',
            },
        ),
    ]
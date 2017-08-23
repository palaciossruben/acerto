# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-23 15:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0013_user_is_mobile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('experience', models.IntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.Country')),
                ('education', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.Education')),
                ('profession', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.Profession')),
            ],
            options={
                'db_table': 'campaigns',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='campaign_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beta_invite.Campaign'),
        ),
    ]

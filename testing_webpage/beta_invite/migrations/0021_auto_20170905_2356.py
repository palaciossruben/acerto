# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-05 23:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0020_tradeuser_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulletType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'bullet_types',
            },
        ),
        migrations.CreateModel(
            name='CampaignBullet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_es', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'campaign_bullets',
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='title_es',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='campaignbullet',
            name='campaign',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.Campaign'),
        ),
        migrations.AddField(
            model_name='campaignbullet',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beta_invite.BulletType'),
        ),
    ]

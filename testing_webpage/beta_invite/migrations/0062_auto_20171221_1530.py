# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-21 15:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0061_campaign_calendly_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsent',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='beta_invite.Campaign'),
        ),
        migrations.AlterField(
            model_name='emailsent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='beta_invite.User'),
        ),
    ]

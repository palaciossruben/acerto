# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-15 22:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('beta_invite', '0158_city_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]

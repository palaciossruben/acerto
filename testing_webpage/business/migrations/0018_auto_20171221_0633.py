# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-21 06:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0017_businessuser_campaigns'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='country',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='education',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='profession',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
    ]

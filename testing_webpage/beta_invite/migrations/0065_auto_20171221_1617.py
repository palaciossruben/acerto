# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-21 16:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0064_auto_20171221_1610'),
    ]

    database_operations = [
        migrations.AlterModelTable('EmailSent', 'testing_webpage_emailsent')
    ]

    state_operations = [
        migrations.DeleteModel('EmailSent')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]

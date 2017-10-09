# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-28 23:27
from __future__ import unicode_literals

from django.db import migrations


def fixes_previous_migration_bug(apps, schema_editor):
    # Some comments where left empty, should be removed.
    comment_class = apps.get_model('dashboard', 'Comment')

    for comment in comment_class.objects.all():
        if comment.text == '':
            comment.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_auto_20170928_1950'),
    ]

    operations = [
        migrations.RunPython(fixes_previous_migration_bug),
    ]

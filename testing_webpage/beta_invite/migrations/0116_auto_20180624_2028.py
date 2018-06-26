# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-24 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0115_auto_20180624_0043'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cut_score', models.FloatField(null=True)),
                ('final_score', models.FloatField(null=True)),
                ('cognitive_score', models.FloatField(null=True)),
                ('technical_score', models.FloatField(null=True)),
                ('requirements_score', models.FloatField(null=True)),
                ('soft_skills_score', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evaluation_summaries', models.ManyToManyField(to='beta_invite.EvaluationSummary')),
            ],
            options={
                'db_table': 'summary_evaluations',
            },
        ),
        migrations.RemoveField(
            model_name='evaluation',
            name='campaign',
        ),
        migrations.AddField(
            model_name='evaluationsummary',
            name='evaluations',
            field=models.ManyToManyField(to='beta_invite.Evaluation'),
        ),
    ]

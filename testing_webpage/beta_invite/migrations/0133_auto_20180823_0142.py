# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-08-23 01:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beta_invite', '0132_auto_20180815_0305'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='applicant_evaluation_last',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applicant_evaluation_last', to='beta_invite.EvaluationSummary'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='recommended_evaluation_last',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommended_evaluation_last', to='beta_invite.EvaluationSummary'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='rejected_evaluation_last',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rejected_evaluation_last', to='beta_invite.EvaluationSummary'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='relevant_evaluation_last',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='relevant_evaluation_last', to='beta_invite.EvaluationSummary'),
        ),
    ]
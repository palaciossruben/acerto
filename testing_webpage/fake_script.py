"""
Add fake averages to show some value on old campaign
"""

import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from beta_invite.models import Campaign, EvaluationSummary


makers = Campaign.objects.get(pk=76)


recommended_evaluation = EvaluationSummary()
relevant_evaluation = EvaluationSummary()
applicant_evaluation = EvaluationSummary()

recommended_evaluation.cognitive_score = 0.92
recommended_evaluation.technical_score = 0.85
recommended_evaluation.requirements_score = 0.87
recommended_evaluation.soft_skills_score = 0.82
recommended_evaluation.save()

relevant_evaluation.cognitive_score = 0.82
relevant_evaluation.technical_score = 0.71
relevant_evaluation.requirements_score = 0.83
relevant_evaluation.soft_skills_score = 0.81
relevant_evaluation.save()

applicant_evaluation.cognitive_score = 0.62
applicant_evaluation.technical_score = 0.55
applicant_evaluation.requirements_score = 0.45
applicant_evaluation.soft_skills_score = 0.47
applicant_evaluation.save()


makers.recommended_evaluation = recommended_evaluation
makers.relevant_evaluation = relevant_evaluation
makers.applicant_evaluation = applicant_evaluation

makers.save()

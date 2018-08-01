"""
Learns the importance of each question separating the candidates
"""
import os
import sys

from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import pandas as pd
from beta_invite.models import Test, Survey
import common
from dashboard.models import State
from match.pickle_models.pickle_handler import save_model, load_model
from match import common_learning, learn, text_match, clustering
from match.pickle_models import pickle_handler

"""
user = models.ForeignKey(User, null=True)
campaign = models.ForeignKey(Campaign, null=True)
test = models.ForeignKey(Test, null=True)
question = models.ForeignKey(Question)
answer = models.ForeignKey(Answer, null=True, on_delete=models.SET_NULL)
text_answer = models.CharField(max_length=10000, null=True)
numeric_answer = models.FloatField(null=True)
interview = models.ForeignKey(Interview, null=True)
video_token = models.CharField(max_length=200, null=True)
score = models.FloatField(null=True)
try_number = models.IntegerField(default=1)

created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
"""

"""
candidates = {key: value}
where:
    key = candidate
    value = {question: passed}
        where: passed = 1 if survey.score > survey.test.cut_score else 0
"""

candidates = dict()
cognitive_test = Test.objects.get(name='Cognitive Test')
surveys = Survey.objects.filter(test=cognitive_test)
question_ids = [q.id for q in cognitive_test.questions.all()]

for survey in surveys:

    if survey.score and survey.test.cut_score:
        #print(survey.user)
        #print(survey.campaign)
        candidate = common.get_candidate(survey.user, survey.campaign)

        if candidate:
            print(survey.score)
            print(survey.test.cut_score/100)
            passed = 1 if survey.score > survey.test.cut_score/100 else 0

            if candidates.get(candidate) is None:
                candidates[candidate] = dict()

            candidates[candidate][survey.question] = passed

print(candidates)

df = pd.DataFrame(columns=question_ids + ['passed'], index=[c.id for c in candidates.keys()])


for candidate, values in candidates.items():
    passed_test = 1 if candidate.state in State.get_relevant_states() else 0
    for question, passed in values.items():
        df.loc[candidate.id, question.id] = passed

print(df)



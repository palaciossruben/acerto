import os
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

from django.test import TestCase
from business.models import Campaign
from business import search_module
import common


# distribution by position of clicks on google search results:
# https://searchenginewatch.com/sew/study/2276184/no-1-position-in-google-gets-33-of-search-traffic-study
# The value is a percentage of clicks from the total and the position is the position on the search results.
SEARCH_BY_POSITION = [
    0.325,
    0.176,
    0.114,
    0.081,
    0.061,
    0.044,
    0.035,
    0.031,
    0.026,
    0.024
]


class YourTestClass(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_score(self):
        campaigns = Campaign.objects.all()

        for campaign in campaigns:
            search_text = search_module.clean_text_for_search(campaign.get_search_text())
            users = search_module.get_top_matching_users(search_text)
            candidates = [common.get_candidate(user, campaign) for user in users]

        return 3

    def get_strategy_result(self, strategy):
        if strategy == 'a':
            return self.get_score()
        else:
            with open('past_result.txt', 'r') as f:
                try:
                    return int(f.read())
                except ValueError:
                    return 0

    def get_improvement(self, a, b):
        if b != 0:
            return round((a-b)/b*100, 2)
        else:
            return None

    def test_AB_testing(self):
        a = self.get_strategy_result('a')
        b = self.get_strategy_result('b')
        self.assertGreater(a, b)
        improvement = self.get_improvement(a, b)
        print('a_score: {a}\nb_score: {b}\nimprovement: {i}%'.format(a=a, b=b, i=improvement))

        with open('past_result.txt', 'w') as f:
            f.write(str(a))

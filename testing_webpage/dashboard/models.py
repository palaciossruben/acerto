import statistics
import numpy as np
from django.db import models
from django.db.models.signals import post_init

from beta_invite.models import User, Campaign, Evaluation, Survey, EvaluationSummary, Score
from dashboard import constants as cts
from beta_invite.util import common_senders
from business.models import BusinessUser


class State(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, default='BL')
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'states'

    def looks_good(self):
        return self.code in ('STC', 'GTJ', 'DI')

    def passed_interview(self):
        return self.code in ('STC', 'GTJ', 'DI', 'RBC')

    def got_the_job(self):
        return self.code in 'GTJ'

    def passed_test(self):
        return self.looks_good() or self.code in ('WFI', 'ROI', 'RBC')

    @staticmethod
    def get_relevant_states():
        return [s for s in State.objects.filter(code__in=['WFI', 'DI'])]

    @staticmethod
    def get_recommended_states():
        return [s for s in State.objects.filter(code__in=['GTJ', 'STC'])]

    @staticmethod
    def get_applicant_states():
        return [s for s in State.objects.filter(code__in=['P', 'BL'])]

    @staticmethod
    def get_rejected_states():
        return [s for s in State.objects.filter(code__in=['ROI', 'RBC', 'SR', 'FT', 'ROT', ])]

    @staticmethod
    def get_rejected_by_human_states():
        return [s for s in State.objects.filter(code__in=['ROI', 'RBC', 'SR', ])]


class Comment(models.Model):

    text = models.CharField(max_length=10000, null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'comments'


class Screening(models.Model):

    name = models.CharField(max_length=200)
    passed = models.BooleanField()

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.pk, self.name, self.passed)

    # adds custom table name
    class Meta:
        db_table = 'screenings'


class Candidate(models.Model):
    """
    This model should be unique for any (user, campaign) pair. A ser can have multiple candidacies in different
    campaigns. But no user can have more than one candidate object in the same campaign.
    """

    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, default=cts.DEFAULT_STATE)
    removed = models.BooleanField(default=False)
    salary = models.CharField(max_length=100, default='')
    comments = models.ManyToManyField(Comment, default=[])
    evaluations = models.ManyToManyField(Evaluation)
    evaluation_summary = models.ForeignKey(EvaluationSummary, null=True)
    surveys = models.ManyToManyField(Survey)
    text_match = models.FloatField(null=True, default=None)
    match_regression = models.FloatField(null=True, default=None)
    match_classification = models.IntegerField(null=True, default=None)
    screening = models.ForeignKey(Screening, null=True, on_delete=models.SET_NULL)
    screening_explanation = models.CharField(max_length=200, default='')
    rating = models.IntegerField(null=True)
    mean_scores = models.ManyToManyField(Score, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.pk, self.user.name, self.campaign.name)

    # adds custom table name
    class Meta:
        db_table = 'candidates'

    def update_mean_test_scores(self):
        """
        Gets a mean value for each test taken.
        :return:
        """

        mean_scores_dict = dict()
        for e in self.evaluations.all():
            for s in e.scores.all():
                values = mean_scores_dict.get(s.test_id, [])
                values.append(s.value)
                mean_scores_dict[s.test_id] = values

        mean_scores = []
        for test_id, values in mean_scores_dict.items():
            new_score = Score(test_id=test_id, value=statistics.mean(values))
            new_score.save()
            mean_scores.append(new_score)

        self.mean_scores = mean_scores
        self.save()

    def get_evaluation_summary(self):
        """
        Retrieve summary or try calculating it.
        :return:
        """
        if self.evaluation_summary:
            return self.evaluation_summary
        else:
            self.evaluation_summary = EvaluationSummary.create(self.evaluations.all())
            return self.evaluation_summary

    def get_business_user(self):
        """
        Given a campaign gets the business_user if it exists, else None
        :return: business_user or None
        """

        business_users = [b for b in BusinessUser.objects.filter(campaign=self.campaign)]

        if len(business_users) > 0:
            return business_users[0]
        else:
            return np.nan

    def get_average_final_score(self):
        evaluations = self.evaluations.all()

        if evaluations:
            return statistics.mean([e.final_score for e in evaluations])
        else:
            return 0

    def get_text_match(self):
        if self.text_match:
            return self.text_match
        return np.nan

    def get_education_level(self):
        if self.user and self.user.education:
            return self.user.education.level
        return np.nan

    def get_profession_id(self):
        if self.user and self.user.profession:
            return self.user.profession_id
        return np.nan

    def get_country_id(self):
        if self.user and self.user.country:
            return self.user.country_id
        return np.nan

    def get_city_id(self):
        if self.user and self.user.city:
            return self.user.city_id
        return np.nan

    def get_campaign_country_id(self):
        if self.campaign:
            return self.campaign.country_id
        return np.nan

    def get_campaign_city_id(self):
        if self.campaign:
            return self.campaign.city_id
        return np.nan

    def get_campaign_profession_id(self):
        if self.campaign:
            return self.campaign.profession_id
        return np.nan

    def get_campaign_education_level(self):
        if self.campaign and self.campaign.education:
            return self.campaign.education.level
        return np.nan

    def get_profession_name(self):
        if self.user and self.user.profession:
            return self.user.profession.name
        return np.nan

    def get_education_name(self):
        if self.user and self.user.education:
            return self.user.education.name
        return np.nan

    def get_country_name(self):
        if self.user and self.user.country:
            return self.user.country.name
        return np.nan

    def get_city_name(self):
        if self.user and self.user.city:
            return self.user.city.name
        return np.nan


class BusinessState(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200)
    states = models.ManyToManyField(State)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'business_states'


class Message(models.Model):
    """
    This table stores messages sent later on. is a kind of queue
    """

    candidate = models.ForeignKey(Candidate, null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=10000, default='')
    sent = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=200, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'messages'

    def add_format_and_mark_as_sent(self):
        """
        Adds format to message and returns itself
        :return: self
        """
        candidate = self.candidate
        params = common_senders.get_params_with_candidate(candidate, candidate.user.language_code, {})
        self.text = self.text.format(**params)
        self.sent = True
        self.save()
        return self


def message_post_init(**kwargs):
    instance = kwargs.get('instance')
    instance.contact_name = instance.candidate.user.name + ' ' + str(instance.candidate.user.pk)


post_init.connect(message_post_init, Message)

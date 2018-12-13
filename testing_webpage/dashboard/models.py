import statistics
import numpy as np
import traceback

from django.db import models
from django.db.models.signals import post_init
from django.contrib.auth.models import User as AuthUser

from beta_invite.models import User, Campaign, Evaluation, Survey, EvaluationSummary, Score, Test
from dashboard import constants as cts
from beta_invite.util import common_senders


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

    # IMPORTANT: These states must speak perfectly with business_states.json, must be homologous

    @staticmethod
    def get_recommended_state_codes():
        return ['GTJ', 'STC', 'ABC']

    @staticmethod
    def get_relevant_state_codes():
        return ['WFI', 'DI', 'GTJ', 'STC', 'ABC']

    @staticmethod
    def get_applicant_state_codes():
        return ['P', 'BL', 'RBC', 'SR', 'FT', 'ROT', 'ROI']

    @staticmethod
    def get_rejected_state_codes():
        return ['ROI', 'RBC', 'SR', 'FT', 'ROT']

    @staticmethod
    def get_rejected_by_human_state_codes():
        return ['ROI', 'RBC', 'SR']

    @staticmethod
    def get_human_intervention_state_codes():
        return ['DI']

    @staticmethod
    def get_recommended_states():
        return list(State.objects.filter(code__in=State.get_recommended_state_codes()))

    @staticmethod
    def get_relevant_states():
        return list(State.objects.filter(code__in=State.get_relevant_state_codes()))

    @staticmethod
    def get_applicant_states(): 
        return list(State.objects.filter(code__in=State.get_applicant_state_codes()))

    @staticmethod
    def get_rejected_states():
        return list(State.objects.filter(code__in=State.get_rejected_state_codes()))

    @staticmethod
    def get_rejected_by_human_states():
        return list(State.objects.filter(code__in=State.get_rejected_by_human_state_codes()))

    @staticmethod
    def get_human_intervention_states():
        return list(State.objects.filter(code__in=State.get_human_intervention_state_codes())) +\
               State.get_recommended_states() +\
               State.get_rejected_by_human_states()


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


class StateEvent(models.Model):
    """
    Any change in state is logged here.
    """

    from_state = models.ForeignKey(State, related_name='from_state')
    to_state = models.ForeignKey(State, related_name='to_state')
    auth_user = models.ForeignKey(AuthUser, null=True, on_delete=models.SET_NULL)
    automatic = models.BooleanField(default=False)
    forecast = models.NullBooleanField(default=None, null=True)
    place = models.TextField(null=True)
    use_machine_learning = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, from_state, to_state, auth_user, forecast, place, use_machine_learning):
        """
        If no auth user is given then it is a automated event.
        """

        state_event = cls(from_state=from_state,
                          to_state=to_state,
                          auth_user=auth_user,
                          automatic=True if auth_user is None else False,
                          forecast=forecast,
                          place=place,
                          use_machine_learning=use_machine_learning)
        state_event.save()

        return state_event

    def __str__(self):
        return 'from: {0}\nto: {1}\non: {2}\nautomatic: {3}\nforecast: {4}\nuser: {5}\nplace: {6}'.format(self.from_state,
                                                                                                          self.to_state,
                                                                                                          self.created_at,
                                                                                                          self.automatic,
                                                                                                          self.forecast,
                                                                                                          self.auth_user,
                                                                                                          self.place)

    # adds custom table name
    class Meta:
        db_table = 'state_events'


def exception_to_string(exception):
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(exception.__traceback__)  # add limit=??
    pretty = traceback.format_list(stack)
    return ''.join(pretty) + '\n  {} {}'.format(exception.__class__, exception)


class Candidate(models.Model):
    """
    This model should be unique for any (user, campaign) pair. A ser can have multiple candidacies in different
    campaigns. But no user can have more than one candidate object in the same campaign.
    """

    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, default=cts.DEFAULT_STATE)
    removed = models.BooleanField(default=False)
    sent_to_client = models.BooleanField(default=False)
    salary = models.CharField(max_length=100, default='')
    comments = models.ManyToManyField(Comment, default=[])
    evaluations = models.ManyToManyField(Evaluation)
    evaluation_summary = models.ForeignKey(EvaluationSummary, null=True)
    surveys = models.ManyToManyField(Survey)
    text_match = models.FloatField(null=True, default=None)
    match_classification = models.IntegerField(null=True, default=None)
    screening = models.ForeignKey(Screening, null=True, on_delete=models.SET_NULL)
    screening_explanation = models.CharField(max_length=200, default='')
    rating = models.IntegerField(null=True)
    mean_scores = models.ManyToManyField(Score)
    state_events = models.ManyToManyField(StateEvent)
    change_by_client = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    last_evaluation = models.ForeignKey(Evaluation, null=True, related_name='last_evaluation')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.pk, self.user.name, self.campaign.name)

    # adds custom table name
    class Meta:
        db_table = 'candidates'

    def get_last_requirement_surveys(self):

        surveys = []
        last_evaluation = self.get_last_evaluation()
        for score in last_evaluation.scores.filter(test__type__name='requirements'):
            for question in score.test.questions.all():
                surveys.append(Survey.get_last_try_with_candidate(self, score.test, question))

        return surveys

    # TODO: add traceback to default place... wow, great idea!
    def change_state(self, state_code, auth_user=None, place=None, forecast=None, use_machine_learning=False):
        """
        from one state to another everything is logged for debugging and further analysis
        :param state_code: the code, its a str defined in the State model
        :param auth_user: Django users
        :param place: open description of the place where stuff is happening!
        :param forecast: boolean, indicating AI decision
        :param use_machine_learning: Boolean, is it using machine learning???
        :return: None
        """
        if place is None:
            try:
                raise ValueError
            except ValueError as e:
                place = ''.join(exception_to_string(e).split('testing_webpage')[3:])

        to_state = State.objects.get(code=state_code)

        event = StateEvent.create(from_state=self.state,
                                  to_state=to_state,
                                  auth_user=auth_user,
                                  forecast=forecast,
                                  place=place,
                                  use_machine_learning=use_machine_learning)
        if auth_user is None:
            event.automatic = True
        event.save()

        self.state = to_state
        self.state_events.add(event)
        self.save()

    def get_last_evaluation(self):
        if self.last_evaluation is None:
            try:
                return self.evaluations.latest('created_at')
            except models.ObjectDoesNotExist:
                return None
        else:
            return self.last_evaluation

    def get_last_score(self):

        e = self.get_last_evaluation()
        if e:
            return e.final_score
        else:
            return None

    def get_last_cut_score(self):

        e = self.get_last_evaluation()
        if e:
            return e.cut_score
        else:
            return None

    def print_attribute(self, attribute):

        last_evaluation = self.get_last_evaluation()

        if last_evaluation and getattr(last_evaluation, attribute):
            return int(getattr(last_evaluation, attribute))
        else:
            return ''

    def print_cultural_fit_score(self):
        return self.print_attribute('cultural_fit_score')

    def print_motivation_score(self):
        return self.print_attribute('motivation_score')

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
            new_score = Score.create(test=Test.objects.get(pk=test_id),
                                     value=statistics.mean(values),)
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
            self.save()
            return self.evaluation_summary

    def get_last_evaluation_attr(self, attr):
        if self.get_last_evaluation():
            return getattr(self.get_last_evaluation(), attr)
        else:
            return None

    def get_evaluation_summary_attr(self, attr):
        if self.get_evaluation_summary():
            return getattr(self.get_evaluation_summary(), attr)
        else:
            return None

    def get_average_cognitive_score(self):
        return self.get_evaluation_summary_attr('cognitive_score')

    def get_average_technical_score(self):
        return self.get_evaluation_summary_attr('technical_score')

    def get_average_requirements_score(self):
        return self.get_evaluation_summary_attr('requirements_score')

    def get_average_motivation_score(self):
        return self.get_evaluation_summary_attr('motivation_score')

    def get_average_cultural_fit_score(self):
        return self.get_evaluation_summary_attr('cultural_fit_score')

    def get_last_cognitive_score(self):
        return self.get_last_evaluation_attr('cognitive_score')

    def get_last_technical_score(self):
        return self.get_last_evaluation_attr('technical_score')

    def get_last_requirements_score(self):
        return self.get_last_evaluation_attr('requirements_score')

    def get_last_motivation_score(self):
        return self.get_last_evaluation_attr('motivation_score')

    def get_last_cultural_fit_score(self):
        return self.get_last_evaluation_attr('cultural_fit_score')

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
    description = models.CharField(max_length=200, null=True)
    description_es = models.CharField(max_length=200, null=True)

    def translate(self, lang_code):
        if lang_code == 'es':
            self.name = self.name_es
            self.description = self.description_es

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
    filename = models.CharField(max_length=200, null=True)  # the filename of the message, so messages will not repeat

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
        params = common_senders.get_params_with_candidate(self.candidate,
                                                          self.candidate.user.language_code,
                                                          {})
        self.text = self.text.format(**params)
        self.sent = True
        self.save()
        return self


def message_post_init(**kwargs):
    instance = kwargs.get('instance')
    instance.contact_name = instance.candidate.user.name + ' ' + str(instance.candidate.user.pk)


post_init.connect(message_post_init, Message)

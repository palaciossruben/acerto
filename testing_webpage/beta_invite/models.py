import re

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from beta_invite import constants as cts


class Visitor(models.Model):

    ip = models.GenericIPAddressField(null=True)
    is_mobile = models.NullBooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.ip, self.created_at)

    # adds custom table name
    class Meta:
        db_table = 'visitors'


class ProfessionType(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'profession_types'


class Profession(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    type = models.ForeignKey(ProfessionType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'professions'


class WorkAreaType(models.Model):
    """
    Groups similar workAreas
    """
    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'work_area_types'


class WorkArea(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    type = models.ForeignKey(WorkAreaType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'work_areas'


class Gender(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    sex = models.IntegerField()

    def __str__(self):
        return '{0}, sex: {1}'.format(self.name, self.sex)

    # adds custom table name
    class Meta:
        db_table = 'genders'


class Education(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    level = models.IntegerField()

    def __str__(self):
        return '{0}, level: {1}'.format(self.name, self.level)
    # adds custom table name

    class Meta:
        db_table = 'education'


class Country(models.Model):

    name = models.CharField(max_length=200)
    calling_code = models.IntegerField(null=True)
    language_code = models.CharField(max_length=3, default='en')
    ISO = models.CharField(max_length=2, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'countries'


class City(models.Model):

    name = models.CharField(max_length=200, null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'cities'


class BulletType(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'bullet_types'


class Bullet(models.Model):

    name = models.CharField(max_length=1000)
    name_es = models.CharField(max_length=1000)
    bullet_type = models.ForeignKey(BulletType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'bullets'


class QuestionType(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'question_types'


class Answer(models.Model):

    name = models.CharField(max_length=1000)
    name_es = models.CharField(max_length=1000, null=True)
    order = models.IntegerField(null=True)  # TODO default=1?

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    def duplicate(self):
        """Duplicates answer"""
        self.pk = None
        self.save()

    # adds custom table name
    class Meta:
        db_table = 'answers'
        ordering = ['order']


class Question(models.Model):

    text = models.CharField(max_length=1000, null=True)
    text_es = models.CharField(max_length=1000, null=True)
    answers = models.ManyToManyField(Answer)
    type = models.ForeignKey(QuestionType, null=True, on_delete=models.SET_NULL)
    correct_answers = models.ManyToManyField(Answer, related_name='correct_answers')
    image_path = models.CharField(max_length=200, null=True)
    order = models.IntegerField(default=1)
    params = JSONField(null=True)
    video_token = models.CharField(max_length=200, null=True)
    excluding = models.BooleanField(default=False)  # if wrong answer then fails tests

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'questions'
        ordering = ['order']

    def translate(self, lang_code):
        """
        Args:
            self: Me
            lang_code: 'es' for example
        Returns: translates
        """
        if lang_code == 'es':
            self.text = self.text_es

    def remove_answer_gaps(self):
        """
        Removes gaps in the order of answers, that can happen if some answers have been deleted.
        Uses the fact that answers are retrieved by asc 'order' variable.
        :return: nothing
        """
        for idx, a in enumerate(self.answers.all()):
            a.order = idx + 1
            a.save()

    def duplicate(self):

        answers = self.answers.all()
        question_type = self.type
        old_correct_answers = self.correct_answers.all()

        # Creates new question
        self.pk = None
        self.save()

        for a in answers:

            is_correct_answer = False
            if a in old_correct_answers:
                is_correct_answer = True

            a.duplicate()
            self.answers.add(a)

            if is_correct_answer:
                self.correct_answers.add(a)

        self.type = question_type
        self.save()


class TestType(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'test_types'


class Test(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    questions = models.ManyToManyField(Question)
    cut_score = models.IntegerField(default=70)
    type = models.ForeignKey(TestType, default=None, null=True)
    feedback_url = models.CharField(max_length=200,
                                    default='',
                                    null=True)
    excluding = models.BooleanField(default=False)  # if didn't passed the test, then rejects candidate

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    def remove_question_gaps(self):
        """
        Removes gaps in the order of questions, that can happen if some questions have been deleted.
        Uses the fact that questions are retrieved by asc 'order' variable.
        :return: nothing
        """
        for idx, q in enumerate(self.questions.all()):
            q.order = idx + 1
            q.save()

    def duplicate_questions(self, questions):
        """Adds Duplicated Questions"""

        for q in questions:
            q.duplicate()
            self.questions.add(q)
        self.save()

    def duplicate(self):
        self.name = self.name + ' (1)'
        self.name_es = self.name_es + ' (1)'
        questions = self.questions.all()

        # Creates new test
        self.pk = None
        self.save()

        self.duplicate_questions(questions)

    @classmethod
    def get_all(cls):
        """sort in alphabetical order"""
        return sorted(cls.objects.all(), key=lambda test: test.name)

    # adds custom table name
    class Meta:
        db_table = 'tests'


class Score(models.Model):

    test = models.ForeignKey(Test)
    value = models.FloatField()
    passed = models.NullBooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, test, value):
        """
        Instead of:
        score = Score(...)
        do
        score = Score.create(...)

        This is a convenience method to calculate self.passing upon creation:
        https://stackoverflow.com/questions/843580/writing-a-init-function-to-be-used-in-django-model
        And
        https://stackoverflow.com/questions/20569910/how-to-initialize-an-empty-object-with-foreignkey-in-django
        :return:
        """

        score = cls(value=value, test=test)

        if score.value and score.test:
            score.passed = score.value >= score.test.cut_score

        score.save()

        return score

    def __str__(self):
        return 'id={0}, test={1}, value={2}'.format(self.pk, self.test, self.value)

    # adds custom table name
    class Meta:
        db_table = 'scores'


class Evaluation(models.Model):
    """
    Summary of all tests results for a given user.
    """

    cut_score = models.FloatField(null=True)
    final_score = models.FloatField(null=True)
    passed = models.NullBooleanField(null=True)
    scores = models.ManyToManyField(Score)

    cognitive_score = models.FloatField(null=True)
    technical_score = models.FloatField(null=True)
    requirements_score = models.FloatField(null=True)
    soft_skills_score = models.FloatField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, scores):
        """
        Instead of:
        evaluation = Evaluation(...)
        do
        evaluation = Evaluation.create(...)

        This is a convenience method to save Foreign keys with out having a mess outside see:
        https://stackoverflow.com/questions/843580/writing-a-init-function-to-be-used-in-django-model
        And
        https://stackoverflow.com/questions/20569910/how-to-initialize-an-empty-object-with-foreignkey-in-django
        :param scores: List of scores objects
        :return:
        """

        evaluation = cls()
        evaluation.save()
        evaluation.scores = scores

        # Saves first in order to have an id and assign the scores.
        evaluation.save()

        return evaluation

    def __str__(self):
        return 'id={0}, cut_score={1}, value={2}, passed={3}'.format(self.pk,
                                                                     self.cut_score,
                                                                     self.final_score,
                                                                     self.passed)

    def get_score_for_test_type(self, type_name):
        test_type = TestType.objects.get(name=type_name)
        return average_list([s.value for s in self.scores.all() if s.test.type == test_type])

    # adds custom table name
    class Meta:
        db_table = 'evaluations'


class EvaluationSummary(models.Model):
    """
    Summary of all evaluations or other EvaluationSummaries.
    """

    cut_score = models.FloatField(null=True)
    final_score = models.FloatField(null=True)

    cognitive_score = models.FloatField(null=True)
    technical_score = models.FloatField(null=True)
    requirements_score = models.FloatField(null=True)
    soft_skills_score = models.FloatField(null=True)

    evaluations = models.ManyToManyField(Evaluation)
    evaluation_summaries = models.ManyToManyField("self", symmetrical=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, evaluations):
        """
        Instead of:
        evaluation = Evaluation(...)
        do
        evaluation = Evaluation.create(...)

        This is a convenience method to save Foreign keys with out having a mess outside see:
        https://stackoverflow.com/questions/843580/writing-a-init-function-to-be-used-in-django-model
        And
        https://stackoverflow.com/questions/20569910/how-to-initialize-an-empty-object-with-foreignkey-in-django
        :param evaluations: List of evaluation objects
        :return:
        """

        evaluation_summary = cls()

        # Saves first in order to have an id and assign the scores.
        evaluation_summary.save()
        evaluation_summary.update_evaluations(evaluations)

        return evaluation_summary

    def __str__(self):
        return 'id={0}, cut_score={1}, cognitive_score={2}'.format(self.pk,
                                                                   self.cut_score,
                                                                   self.cognitive_score)

    def update_evaluations(self, evaluations):
        """
        :param evaluations: can be Evaluation or EvaluationSummary objects
        :return: None
        """

        if len(evaluations) > 0:

            if isinstance(evaluations[0], Evaluation):
                self.evaluations = evaluations
            elif isinstance(evaluations[0], EvaluationSummary):
                self.evaluation_summaries = evaluations
            else:
                raise NotImplementedError

            self.cut_score = average_list([e.cut_score for e in evaluations])
            self.final_score = average_list([e.final_score for e in evaluations])

            self.cognitive_score = average_list([e.cognitive_score for e in evaluations])
            self.technical_score = average_list([e.technical_score for e in evaluations])
            self.requirements_score = average_list([e.requirements_score for e in evaluations])
            self.soft_skills_score = average_list([e.soft_skills_score for e in evaluations])
            # TODO: add any new score here

        self.save()

    # adds custom table name
    class Meta:
        db_table = 'summary_evaluations'


class Interview(models.Model):

    name = models.CharField(max_length=200, null=True)
    name_es = models.CharField(max_length=200, null=True)
    questions = models.ManyToManyField(Question)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'interviews'


class Seniority(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'seniorities'

    def __str__(self):
        return '{0}'.format(self.name)


class JobFunctions(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'job_functions'

    def __str__(self):
        return '{0}'.format(self.name)


class Campaign(models.Model):

    name = models.CharField(max_length=200)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education = models.ForeignKey(Education, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=5000, null=True)
    description_es = models.CharField(max_length=5000, null=True)
    title = models.CharField(max_length=200, null=True)
    title_es = models.CharField(max_length=200, null=True)
    bullets = models.ManyToManyField(Bullet)
    tests = models.ManyToManyField(Test)
    interviews = models.ManyToManyField(Interview)
    calendly = models.BooleanField(default=True)
    active = models.BooleanField(default=False)
    calendly_url = models.CharField(max_length=200, default=cts.INTERVIEW_CALENDLY)
    removed = models.BooleanField(default=False)
    free_trial = models.BooleanField(default=True)
    seniority = models.ForeignKey(Seniority, null=True)
    job_function = models.ForeignKey(JobFunctions, null=True)
    has_email = models.BooleanField(default=True)
    work_area = models.ForeignKey(WorkArea, null=True, on_delete=models.SET_NULL)
    operational_efficiency = models.FloatField(null=True)

    recommended_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='recommended_evaluation')
    relevant_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='relevant_evaluation')
    applicant_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='applicant_evaluation')
    rejected_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='rejected_evaluation')

    # TODO: remove circular dependency
    # plan = models.ForeignKey(Plan, null=True, on_delete=models.DO_NOTHING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'campaigns'

    def translate(self, language_code):
        """
        Args:
            self: Me, Myself and I
            language_code: 'es', 'en' etc.
        Returns: Inplace object translation
        """
        if language_code == 'es':
            self.description = self.description_es
            self.title = self.title_es

    def get_host(self):
        return '//127.0.0.1:8000' if settings.DEBUG else 'https://peaku.co'

    def get_url(self):
        return self.get_host()+'/servicio_de_empleo?campaign_id={campaign_id}'.format(campaign_id=self.pk)

    def get_requirement_names(self):
        # TODO: add support for english
        return [b.name_es for b in self.bullets.all() if b.bullet_type and b.bullet_type.name == 'requirement']

    def get_search_text(self):
        return ' '.join([self.title_es] + self.get_requirement_names())


def average_list(my_list):
    """
    Average, if no elements outputs None
    :param my_list:
    :return:
    """
    my_list = [e for e in my_list if e is not None]
    if len(my_list) > 0:
        return sum(my_list) / len(my_list)
    else:
        return None


class User(models.Model):

    email = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True)
    birthday = models.DateField(null=True)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education = models.ForeignKey(Education, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    curriculum_url = models.CharField(max_length=200, default='#')
    curriculum_text = models.TextField(default='')

    # indicates if added to messenger
    added = models.BooleanField(default=False)

    # TODO: deprecated: remove when sure there are no dependencies remaining. Not saving anymore
    campaign = models.ForeignKey(Campaign, null=True)
    phone = models.CharField(max_length=40, null=True)

    # TODO: remove evaluations, this is deprecated. Not saving anymore.
    evaluations = models.ManyToManyField(Evaluation)
    language_code = models.CharField(max_length=3, default='es')

    # Detects if the user is in a mobile phone when registering.
    is_mobile = models.NullBooleanField()

    # Additional info
    gender = models.ForeignKey(Gender, null=True, on_delete=models.SET_NULL)
    programs = models.CharField(max_length=250, null=True)
    work_area = models.ForeignKey(WorkArea, null=True, on_delete=models.SET_NULL)
    salary = models.IntegerField(null=True)
    address = models.CharField(max_length=100, null=True)
    neighborhood = models.CharField(max_length=40, null=True)
    profile = models.CharField(max_length=250, null=True)
    languages = models.CharField(max_length=100, null=True)
    phone2 = models.CharField(max_length=40, null=True)
    phone3 = models.CharField(max_length=40, null=True)
    document = models.CharField(max_length=50, null=True)
    dream_job = models.CharField(max_length=50, null=True)
    hobbies = models.CharField(max_length=250, null=True)
    twitter = models.CharField(max_length=250, null=True)
    facebook = models.CharField(max_length=250, null=True)
    instagram = models.CharField(max_length=250, null=True)
    linkedin = models.CharField(max_length=250, null=True)
    photo_url = models.CharField(max_length=200, default='#')
    brochure_url = models.CharField(max_length=200, default='#')
    politics = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: Make method present on common.py a method of the class User. For this to happen Candidate class has
    # to be moved to testing_webpage to solve circular dependency problem.
    #def get_campaigns(self):
    #    """
    #    Users are unique and have multiple Candidates associated. Each one of which has 1 campaign. This method
    #    returns all campaigns from all Candidates associated to user.
    #    Returns: a list of campaigns where the user is a candidate.
    #    """
    #    return [candidate.campaign for candidate in Candidate.objects.filter(user=self)]

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.email)

    def get_calling_code(self):
        if self.country is not None:
            return str(self.country.calling_code)
        else:  # TODO: SHOULD NEVER DEFAULT to this, Defaults to Colombia
            return str(Country.objects.get(name='Colombia').calling_code)

    def change_to_international_phone_number(self):

        if self.phone:
            # Adds the '+' and country code
            if self.phone[0] != '+':

                self.phone = '+' + self.get_calling_code() + self.phone

                # Adds the '+' only
            elif re.search(r'^' + self.get_calling_code() + '.+', self.phone) is not None:
                self.phone = '+' + self.phone

    # adds custom table name
    class Meta:
        db_table = 'users'


class Survey(models.Model):

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

    @staticmethod
    def get_last_try(campaign, test, question, user):
        surveys = [s for s in Survey.objects.filter(campaign=campaign,
                                                    test=test,
                                                    question=question,
                                                    user=user).order_by('-try_number')]

        if len(surveys) > 0:
            return surveys[0]
        else:
            return None

    @classmethod
    def create(cls, campaign, test_id, question_id, user_id):
        """
        Instead of:
        s = Survey(...)
        do
        s = Survey.create(...)

        see:
        https://stackoverflow.com/questions/843580/writing-a-init-function-to-be-used-in-django-model
        And
        https://stackoverflow.com/questions/20569910/how-to-initialize-an-empty-object-with-foreignkey-in-django
        :return:
        """

        survey = cls(campaign=campaign, test_id=test_id, question_id=question_id)
        if user_id:
            survey.user_id = int(user_id)
            last_survey = Survey.get_last_try(survey.campaign,
                                              survey.test,
                                              survey.question,
                                              survey.user)
            if last_survey:
                survey.try_number = last_survey.try_number + 1
            else:
                survey.try_number = 1

        survey.save()

        return survey

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.pk, self.user, self.test, self.question)

    # adds custom table name
    class Meta:
        db_table = 'surveys'


class PersonalityType(models.Model):

    name = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=2, null=True)
    opposite = models.CharField(max_length=2, null=True)

    def __str__(self):
        return 'id={0}, name={1}, code={2}, opposite={3}'.format(self.pk, self.name, self.code, self.opposite)

    # adds custom table name
    class Meta:
        db_table = 'personality_types'


class EmailType(models.Model):

    name = models.CharField(max_length=200, null=True)

    # True if it has a clock (ie chron tab). False for event driven emails.
    sync = models.NullBooleanField(null=True)

    def __str__(self):
        return 'id={0}, name={1}, sync={2}'.format(self.pk, self.name, self.sync)

    # adds custom table name
    class Meta:
        db_table = 'email_types'

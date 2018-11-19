import re
from datetime import datetime, timedelta
from django.contrib.auth.models import User as AuthUser
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from beta_invite import constants as cts

LOW_SALARY_MARGIN = 0.3
HIGH_SALARY_MARGIN = 0.1


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


class WorkAreaSegment(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=4, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'work_area_segments'


class WorkArea(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    segment = models.ForeignKey(WorkAreaSegment, null=True)
    code = models.CharField(max_length=4, null=True)

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
    alias = models.CharField(max_length=200, null=True)  # Optional alternative name
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

    internal_name = models.CharField(max_length=1500, null=True)
    text = models.CharField(max_length=1500, null=True)
    text_es = models.CharField(max_length=1500, null=True)
    answers = models.ManyToManyField(Answer)
    type = models.ForeignKey(QuestionType, null=True, on_delete=models.SET_NULL)
    correct_answers = models.ManyToManyField(Answer, related_name='correct_answers')
    image_path = models.CharField(max_length=200, null=True)
    order = models.IntegerField(default=1)
    params = JSONField(null=True)
    video_token = models.CharField(max_length=200, null=True)
    excluding = models.BooleanField(default=False)  # if wrong answer then fails tests
    importance = models.FloatField(default=None, null=True)  # coming from RandomForrest
    valid_answer_count = models.IntegerField(default=None, null=True)
    difficulty = models.FloatField(default=None, null=True)

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

    def get_importance(self):
        return '{}%'.format(round(self.importance*100))

    def get_difficulty(self):
        return '{}%'.format(round(self.difficulty*100))


class TestType(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=1, null=True)

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
    public = models.BooleanField(default=False)

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

    def update(self, value):
        """
        Convenience method to update a value from a test
        :param value: the new score
        :return: None
        """
        self.updated_at = datetime.today()
        self.value = value

        if self.value and self.test:
            self.passed = self.value >= self.test.cut_score

        self.save()

    def __str__(self):
        return 'id={0}, test={1}, value={2}'.format(self.pk, self.test.pk, self.value)

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
    motivation_score = models.FloatField(null=True)
    cultural_fit_score = models.FloatField(null=True)
    # TODO: add new score here

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
    motivation_score = models.FloatField(null=True)
    cultural_fit_score = models.FloatField(null=True)
    # TODO: add new score here

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

        # filter None
        evaluations = [e for e in evaluations if e is not None]

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
            self.motivation_score = average_list([e.motivation_score for e in evaluations])
            self.cultural_fit_score = average_list([e.cultural_fit_score for e in evaluations])
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


class CampaignState(models.Model):

    name = models.CharField(max_length=40, null=True)
    name_es = models.CharField(max_length=40, null=True)
    code = models.CharField(max_length=4, null=True)

    # adds custom table name
    class Meta:
        db_table = 'campaign_states'


class Requirement(models.Model):

    name = models.CharField(max_length=200)
    work_area = models.ForeignKey(WorkArea, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'name: {0}, work_area: {1}'.format(self.name, self.work_area)

    # adds custom table name
    class Meta:
        db_table = 'requirements'


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
    requirements = models.ManyToManyField(Requirement)
    interviews = models.ManyToManyField(Interview)
    calendly = models.BooleanField(default=True)
    state = models.ForeignKey(CampaignState, default=2)  # id of Active State, this is NOT NICE
    calendly_url = models.CharField(max_length=200, default=cts.INTERVIEW_CALENDLY)
    removed = models.BooleanField(default=False)
    free_trial = models.BooleanField(default=True)
    seniority = models.ForeignKey(Seniority, null=True)
    job_function = models.ForeignKey(JobFunctions, null=True)
    has_email = models.BooleanField(default=True)
    work_area = models.ForeignKey(WorkArea, null=True, on_delete=models.SET_NULL)
    operational_efficiency = models.FloatField(null=True)
    image = models.CharField(max_length=500, null=True)
    salary_low_range = models.IntegerField(null=True)
    salary_high_range = models.IntegerField(null=True)

    recommended_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='recommended_evaluation')
    relevant_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='relevant_evaluation')
    applicant_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='applicant_evaluation')
    rejected_evaluation = models.ForeignKey(EvaluationSummary, null=True, related_name='rejected_evaluation')

    recommended_evaluation_last = models.ForeignKey(EvaluationSummary, null=True, related_name='recommended_evaluation_last')
    relevant_evaluation_last = models.ForeignKey(EvaluationSummary, null=True, related_name='relevant_evaluation_last')
    applicant_evaluation_last = models.ForeignKey(EvaluationSummary, null=True, related_name='applicant_evaluation_last')
    rejected_evaluation_last = models.ForeignKey(EvaluationSummary, null=True, related_name='rejected_evaluation_last')

    # TODO: remove circular dependency
    # plan = models.ForeignKey(Plan, null=True, on_delete=models.DO_NOTHING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'campaigns'

    def get_work_area_segment(self):
        return self.work_area.segment if self.work_area else None

    @staticmethod
    def print_cop_money(amount):
        reversed_string = [e + (idx % 3 == 0 and idx > 0) * '.' for idx, e in enumerate(reversed(str(amount)))]
        return '$ ' + ''.join(reversed(reversed_string))

    def print_low_salary(self):
        return Campaign.print_cop_money(self.salary_low_range)

    def print_high_salary(self):
        return Campaign.print_cop_money(self.salary_high_range)

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

    def local_date(self):
        date = self.created_at - timedelta(hours=5)

        if date is not None:
            return date
        else:
            return None

    def get_very_low_salary(self):
        if self.salary_low_range:
            return int(self.salary_low_range) * (1 - LOW_SALARY_MARGIN)

    def get_very_high_salary(self):
        if self.salary_high_range:
            return int(self.salary_high_range) * (1 + HIGH_SALARY_MARGIN)


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
    curriculum_text = models.TextField(default=None, null=True)
    curriculum_s3_url = models.CharField(max_length=200, default='#')
    uploaded_to_es = models.BooleanField(default=False)
    added = models.BooleanField(default=False)  # indicates if added to messenger
    phone = models.CharField(max_length=40, null=True)
    language_code = models.CharField(max_length=3, default='es')
    is_mobile = models.NullBooleanField()  # Detects if the user is in a mobile phone when registering.
    google_token = models.CharField(max_length=1000, default=None, null=True)
    auth_user = models.ForeignKey(AuthUser, null=True, on_delete=models.SET_NULL)
    scores = models.ManyToManyField(Score)

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

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.name, self.email, self.pk)

    @staticmethod
    def get_user_from_request(request):
        """
        Given a request that has the AuthUser.id will get the User
        Args:
            request: HTTP request object.
        Returns: A User object.
        """
        return User.objects.get(auth_user_id=request.user.id)

    @staticmethod
    def get_user(user):
        """
        Given a auth User it gets the User
        :param user: Auth User
        :return: Business User or None
        """
        try:
            return User.objects.get(auth_user=user)
        except ObjectDoesNotExist:
            return None

    def get_work_area_segment(self):
        return self.work_area.segment if self.work_area else None

    def get_work_area_segment_code(self):
        s = self.get_work_area_segment()
        if s:
            return s.code
        else:
            return None

    def get_curriculum_url(self):
        """
        Tries S3 first
        :return:
        """

        if self.curriculum_s3_url not in {None, '#'}:
            return self.curriculum_s3_url
        elif self.curriculum_url not in {None, '#'}:  # returns entire url from local machine
            return 'https://peaku.co/static/{url}'.format(url=self.curriculum_url)
        else:
            return '#'

    def get_calling_code(self):
        if self.country is not None:
            return str(self.country.calling_code)
        else:  # TODO: SHOULD NEVER DEFAULT to this, Defaults to Colombia
            return str(Country.objects.get(name='Colombia').calling_code)

    @staticmethod
    def get_short_curriculum_index(short_curriculum):
        """
        Search for first paragraph
        :param short_curriculum: str
        :return: int
        """
        short_curriculum = short_curriculum.lower()

        try:
            search_word = 'perfil profesional'
            return short_curriculum.index(search_word) + len(search_word)
        except ValueError:
            try:
                search_word = 'perfil laboral'
                return short_curriculum.index(search_word) + len(search_word)
            except ValueError:
                try:
                    search_word = 'perfil'
                    return short_curriculum.index(search_word) + len(search_word)
                except ValueError:
                    return None

    def get_short_curriculum(self):

        if self.curriculum_text is None:
            return None

        short_curriculum = self.curriculum_text.replace("\n", "")
        short_curriculum = re.sub(' +', ' ', short_curriculum)
        start_idx = User.get_short_curriculum_index(short_curriculum)

        if start_idx is not None:
            return short_curriculum[start_idx:start_idx + min(250, len(short_curriculum))] + '...'
        else:
            return None

    def get_user_age(self):
        born = datetime(int(self.birthday.strftime("%Y")), int(self.birthday.strftime("%m")), int(self.birthday.strftime("%d")))
        today = datetime.today()
        age = today - born
        seconds_in_a_year = 365*24*60*60
        if age is not None:
            return int(age.total_seconds()/seconds_in_a_year)
        else:
            return None

    # TODO: merge with Lead method, when we have the country of the lead.
    def change_to_international_phone_number(self, add_plus=False):

        plus_symbol = '+' if add_plus else ''

        if self.phone:

            self.phone = self.phone.replace('-', '')

            if self.phone[0] != '+':

                if re.search(r'^' + self.get_calling_code() + '.+', self.phone) is None:

                    self.phone = plus_symbol + self.get_calling_code() + self.phone

                else:
                    self.phone = plus_symbol + self.phone

        return self.phone

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
        survey = Survey.objects.filter(campaign=campaign,
                                       test=test,
                                       question=question,
                                       user=user).order_by('-try_number').first()

        return survey

    @staticmethod
    def get_last_try_with_candidate(candidate, test, question):
        return Survey.get_last_try(candidate.campaign, test, question, candidate.user)

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


class Price(models.Model):

    work_area = models.ForeignKey(WorkArea)
    from_salary = models.IntegerField()
    to_salary = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return 'work_area: {0}, from: {1}, to:{2}, price:{3}'.format(self.work_area,
                                                                     self.from_salary,
                                                                     self.to_salary,
                                                                     self.price)

    # adds custom table name
    class Meta:
        db_table = 'prices'


class RequirementBinaryQuestion(models.Model):

    name = models.CharField(max_length=40, null=True)
    name_es = models.CharField(max_length=40, null=True)
    statement = models.CharField(max_length=400, null=True)
    statement_es = models.CharField(max_length=400, null=True)

    def __str__(self):
        return 'id={0}, name={1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'requirement_binary_questions'


class SearchLog(models.Model):

    campaign = models.ForeignKey(Campaign, default=None, null=True)

    users_from_tests = models.ManyToManyField(User, related_name='tests_search_log')
    users_from_search = models.ManyToManyField(User, related_name='search_search_log')
    users_from_es = models.ManyToManyField(User, related_name='es_search_log')

    all_users = models.ManyToManyField(User, related_name='all_search_log')
    after_salary_filter = models.ManyToManyField(User, related_name='salary_search_log')
    after_city_filter = models.ManyToManyField(User, related_name='city_search_log')
    after_work_area_filter = models.ManyToManyField(User, related_name='work_area_search_log')
    after_cap_filter = models.ManyToManyField(User, related_name='cap_search_log')
    after_recommended_filter = models.ManyToManyField(User, related_name='recommended_search_log')
    after_duplicates_filter = models.ManyToManyField(User, related_name='duplicates_search_log')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return """
        id = {id}
        campaign = {created_at}
        campaign = {campaign}
        users_from_tests = {len_test}
        users_from_search = {len_search}
        users_from_es = {len_es}
        all_users = {len_all}
        after_city_filter = {len_city}
        after_work_area_filter = {len_work_area}
        after_salary_filter = {len_salary}
        after_cap_filter = {len_cap}
        after_recommended_filter = {len_recommended}
        after_duplicates_filter = {len_duplicates}
        """.format(id=self.pk,
                   created_at=self.created_at,
                   campaign=self.campaign.id if self.campaign else None,
                   len_test=len(self.users_from_tests.all()),
                   len_search=len(self.users_from_search.all()),
                   len_es=len(self.users_from_es.all()),
                   len_all=len(self.all_users.all()),
                   len_salary=len(self.after_salary_filter.all()),
                   len_city=len(self.after_city_filter.all()),
                   len_work_area=len(self.after_work_area_filter.all()),
                   len_cap=len(self.after_cap_filter.all()),
                   len_recommended=len(self.after_recommended_filter.all()),
                   len_duplicates=len(self.after_duplicates_filter.all()),
                   )

    # adds custom table name
    class Meta:
        db_table = 'search_logs'

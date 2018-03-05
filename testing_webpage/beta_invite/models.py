import re
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from beta_invite import constants as cts

#from business import Plan


class Visitor(models.Model):

    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)
    is_mobile = models.NullBooleanField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.ip, self.created_at)

    # adds custom table name
    class Meta:
        db_table = 'visitors'


class Profession(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'professions'


class Trade(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'trades'


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

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'countries'


class BulletType(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'bullet_types'


class Bullet(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'answers'


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'questions'

    def translate(self, lang_code):
        """
        Args:
            self: Me
            lang_code: 'es' for example
        Returns: translates
        """
        if lang_code == 'es':
            self.text = self.text_es


class Test(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    questions = models.ManyToManyField(Question)
    cut_score = models.IntegerField(default=70)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'tests'


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
    description = models.CharField(max_length=2000, null=True)
    description_es = models.CharField(max_length=2000, null=True)
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

    # TODO: remove circular dependency
    #plan = models.ForeignKey(Plan, null=True, on_delete=models.DO_NOTHING)

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


class Score(models.Model):

    test = models.ForeignKey(Test)
    value = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, user={1}, test={2}, value={3}'.format(self.pk, self.user, self.test, self.value)

    # adds custom table name
    class Meta:
        db_table = 'scores'


class Evaluation(models.Model):
    """
    Summary of all tests results for a given user.
    """

    campaign = models.ForeignKey(Campaign)
    cut_score = models.FloatField()
    final_score = models.FloatField()
    passed = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scores = models.ManyToManyField(Score)

    # When saving will assign the passed Boolean.
    def save(self, *args, **kwargs):
        if self.passed is None:
            self.passed = (self.final_score >= self.cut_score)
        super(Evaluation, self).save(*args, **kwargs)

    def __str__(self):
        return 'id={0}, cut_score={1}, value={2}, passed={3}'.format(self.pk,
                                                                     self.cut_score,
                                                                     self.final_score,
                                                                     self.passed)

    # adds custom table name
    class Meta:
        db_table = 'evaluations'


class User(models.Model):

    email = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)
    age = models.IntegerField(null=True)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education = models.ForeignKey(Education, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    curriculum_url = models.CharField(max_length=200, default='#')

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.pk, self.user, self.test, self.question)

    # adds custom table name
    class Meta:
        db_table = 'surveys'


class TradeUser(models.Model):

    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=40, null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    trade = models.ForeignKey(Trade, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=1000, null=True)

    # Detects if the user is in a mobile phone when registering.
    is_mobile = models.NullBooleanField()
    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)
    campaign = models.ForeignKey(Campaign, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.email)

    # adds custom table name
    class Meta:
        db_table = 'trade_users'


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

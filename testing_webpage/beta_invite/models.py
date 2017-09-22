from django.db import models


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

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'countries'


class BulletType(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'bullet_types'


class Bullet(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200)
    bullet_type = models.ForeignKey(BulletType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'bullets'


class QuestionType(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'question_types'


class Answer(models.Model):

    name = models.CharField(max_length=1000)
    name_es = models.CharField(max_length=1000, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'answers'


class Question(models.Model):

    text = models.CharField(max_length=1000, null=True)
    text_es = models.CharField(max_length=1000, null=True)
    answers = models.ManyToManyField(Answer)
    type = models.ForeignKey(QuestionType, null=True, on_delete=models.SET_NULL)
    correct_answers = models.ManyToManyField(Answer, related_name='correct_answers')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.text)

    # adds custom table name
    class Meta:
        db_table = 'questions'


class Test(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    questions = models.ManyToManyField(Question)
    cut_score = models.IntegerField(default=70)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'tests'


class Campaign(models.Model):

    name = models.CharField(max_length=200)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education = models.ForeignKey(Education, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=1000, null=True)
    description_es = models.CharField(max_length=1000, null=True)
    title = models.CharField(max_length=200, null=True)
    title_es = models.CharField(max_length=200, null=True)
    bullets = models.ManyToManyField(Bullet)
    tests = models.ManyToManyField(Test)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'campaigns'


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
    campaign = models.ForeignKey(Campaign, null=True)

    # Detects if the user is in a mobile phone when registering.
    is_mobile = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.email)

    # adds custom table name
    class Meta:
        db_table = 'users'


class Survey(models.Model):

    user = models.ForeignKey(User, null=True)
    test = models.ForeignKey(Test)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer, null=True, on_delete=models.SET_NULL)
    text_answer = models.CharField(max_length=10000, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.id, self.user, self.test, self.question)

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

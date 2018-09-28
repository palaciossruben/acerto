import json

from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.contrib.postgres.fields import JSONField

from beta_invite.models import Country, Education, Profession, Campaign


class Plan(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    message = models.CharField(max_length=200, null=True)
    message_es = models.CharField(max_length=200, null=True)
    explanation = models.CharField(max_length=10000, null=True)
    explanation_es = models.CharField(max_length=10000, null=True)
    time = models.IntegerField(default=10)  # number of days.
    candidates = models.IntegerField(default=10)  # candidates: selected applicants
    applicants = models.IntegerField(default=100)  # applicants: people that applied before any filter.
    interview_price = models.CharField(max_length=200, null=True)
    interview_price_es = models.CharField(max_length=200, null=True)
    contract_warranty = models.CharField(max_length=200, null=True)
    contract_warranty_es = models.CharField(max_length=200, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'plans'


class Industry(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'industries'

    def __str__(self):
        return '{0}'.format(self.name)


class Company(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'companies'

    def __str__(self):
        return '{0}'.format(self.name)


class BusinessUser(models.Model):

    email = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=40, null=True)
    campaigns = models.ManyToManyField(Campaign)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    industry = models.ForeignKey(Industry, null=True, on_delete=models.SET_NULL)
    additional_email = models.CharField(max_length=200, null=True)
    # Foreign key to the auth_user table. So that this table can cleanly be in charge of authentication
    auth_user = models.ForeignKey(AuthUser, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.email)

    # adds custom table name
    class Meta:
        db_table = 'business_users'


class Visitor(models.Model):

    ip = models.GenericIPAddressField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.ip, self.created_at)


class Contact(models.Model):

    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=40, null=True)
    message = models.CharField(max_length=5000, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}, {3}'.format(self.name, self.email, self.phone, self.message)

    # adds custom table name
    class Meta:
        db_table = 'contacts'


class Search(models.Model):

    ip = models.GenericIPAddressField(null=True)
    country = models.ForeignKey(Country, null=True)
    profession = models.ForeignKey(Profession, null=True)
    education = models.ForeignKey(Education, null=True)
    experience = models.IntegerField(null=True)
    text = models.CharField(max_length=10000, null=True)
    user_ids = JSONField(null=True)

    def set_user_ids(self, x):
        self.user_ids = json.dumps(x)

    def get_user_ids(self):
        return json.loads(self.user_ids)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id: {0}, ip: {1}, user_ids: {2}'.format(self.pk, self.ip, self.user_ids)

    # adds custom table name
    class Meta:
        db_table = 'searches'


class KeyWord(models.Model):

    name = models.CharField(max_length=20)
    frequency = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'name: {0}, frequency: {1}'.format(self.name, self.frequency)

    # adds custom table name
    class Meta:
        db_table = 'keywords'

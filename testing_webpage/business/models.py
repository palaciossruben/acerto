import json

from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.contrib.postgres.fields import JSONField

from beta_invite.models import Country, Education, Profession


class Plan(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    message = models.CharField(max_length=200, null=True)
    message_es = models.CharField(max_length=200, null=True)
    explanation = models.CharField(max_length=10000, null=True)
    explanation_es = models.CharField(max_length=10000, null=True)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'plans'


class User(models.Model):

    email = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=40, null=True)

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
    ui_version = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.ip, self.created_at)


class Offer(models.Model):

    business_user = models.ForeignKey(User, null=True)
    country = models.ForeignKey(Country, null=True)
    profession = models.ForeignKey(Profession, null=True)
    education = models.ForeignKey(Education, null=True)
    experience = models.IntegerField(null=True)
    skills = JSONField(null=True)

    def set_skills(self, x):
        self.skills = json.dumps(x)

    def get_skills(self):
        return json.loads(self.skills)

    user_ids = JSONField(null=True)

    def set_user_ids(self, x):
        self.user_ids = json.dumps(x)

    def get_user_ids(self):
        return json.loads(self.user_ids)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id: {0}, business_user_id: {1}, user_ids: {2}'.format(self.id, self.business_user, self.user_ids)

    # adds custom table name
    class Meta:
        db_table = 'offers'


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
    skills = JSONField(null=True)

    def set_skills(self, x):
        self.skills = json.dumps(x)

    def get_skills(self):
        return json.loads(self.skills)

    user_ids = JSONField(null=True)

    def set_user_ids(self, x):
        self.user_ids = json.dumps(x)

    def get_user_ids(self):
        return json.loads(self.user_ids)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id: {0}, ip: {1}, user_ids: {2}'.format(self.id, self.ip, self.user_ids)

    # adds custom table name
    class Meta:
        db_table = 'searches'

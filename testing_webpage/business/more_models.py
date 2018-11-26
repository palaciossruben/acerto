"""Here lies models that can be impoted both in beta_invite and business!"""
from django.db import models


class Company(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'companies'

    def __str__(self):
        return '{0}'.format(self.name)


class School(models.Model):

    name = models.CharField(max_length=200)

    # adds custom table name
    class Meta:
        db_table = 'schools'

    def __str__(self):
        return '{0}'.format(self.name)

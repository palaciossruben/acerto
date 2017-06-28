from django.db import models


class Visitor(models.Model):

    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)

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


class EducationLevel(models.Model):

    name = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200, null=True)
    level = models.IntegerField()

    def __str__(self):
        return '{0}, level: {1}'.format(self.name, self.level)

    # adds custom table name
    class Meta:
        db_table = 'education_levels'


class Country(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return '{0}'.format(self.name)

    # adds custom table name
    class Meta:
        db_table = 'countries'


class User(models.Model):

    email = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True)
    ui_version = models.CharField(max_length=200)
    age = models.IntegerField(null=True)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education_level = models.ForeignKey(EducationLevel, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    curriculum_url = models.CharField(max_length=200, default='#')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.name, self.email)

    # adds custom table name
    class Meta:
        db_table = 'users'

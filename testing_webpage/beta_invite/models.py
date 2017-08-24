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


class Campaign(models.Model):

    name = models.CharField(max_length=200)
    experience = models.IntegerField(null=True)
    profession = models.ForeignKey(Profession, null=True, on_delete=models.SET_NULL)
    education = models.ForeignKey(Education, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=1000, null=True)
    description_es = models.CharField(max_length=1000, null=True)

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

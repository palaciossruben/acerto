from django.db import models

from beta_invite.models import User, Campaign
from dashboard import constants as cts


class State(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, default='BL')
    priority = models.IntegerField(default=1)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'states'


class Comment(models.Model):

    text = models.CharField(max_length=10000, null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.text)

    # adds custom table name
    class Meta:
        db_table = 'comments'


class Candidate(models.Model):

    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, default=cts.DEFAULT_STATE)

    # TODO: once all comments are migrated to new table then remove comment column.
    comment = models.CharField(max_length=10000, null=True, default='')
    removed = models.BooleanField(default=False)
    salary = models.CharField(max_length=100, default='')
    comments = models.ManyToManyField(Comment, default=[])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.id, self.user.name, self.campaign.name)

    # adds custom table name
    class Meta:
        db_table = 'candidates'



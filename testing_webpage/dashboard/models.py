from django.db import models

from beta_invite.models import User, Campaign
from dashboard import constants as cts


class State(models.Model):

    name = models.CharField(max_length=200)
    priority = models.IntegerField(default=1)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return '{0}, {1}'.format(self.id, self.name)

    # adds custom table name
    class Meta:
        db_table = 'states'


class Candidate(models.Model):

    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, default=cts.DEFAULT_STATE)
    comment = models.CharField(max_length=10000, null=True, default='')
    removed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.id, self.user.name, self.campaign.name)

    # adds custom table name
    class Meta:
        db_table = 'candidates'

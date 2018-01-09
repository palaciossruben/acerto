from django.db import models
from django.db.models.signals import post_init

from beta_invite.models import User, Campaign, Evaluation, Survey
from dashboard import constants as cts


class State(models.Model):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, default='BL')
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.name)

    # adds custom table name
    class Meta:
        db_table = 'states'


class Comment(models.Model):

    text = models.CharField(max_length=10000, null=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'comments'


class Candidate(models.Model):
    """
    This model should be unique for any (user, campaign) pair. A ser can have multiple candidacies in different
    campaigns. But no user can have more than one candidate object in the same campaign.
    """

    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, on_delete=models.SET_NULL, default=cts.DEFAULT_STATE)
    removed = models.BooleanField(default=False)
    salary = models.CharField(max_length=100, default='')
    comments = models.ManyToManyField(Comment, default=[])
    evaluations = models.ManyToManyField(Evaluation)
    surveys = models.ManyToManyField(Survey)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.pk, self.user.name, self.campaign.name)

    # adds custom table name
    class Meta:
        db_table = 'candidates'


class Message(models.Model):
    """
    This table stores messages sent later on. is a kind of queue
    """

    candidate = models.ForeignKey(Candidate, null=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=10000, default='')
    sent = models.BooleanField(default=False)
    contact_name = models.CharField(max_length=200, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'messages'


def message_post_init(**kwargs):
    instance = kwargs.get('instance')
    instance.contact_name = instance.candidate.user.name + ' ' + str(instance.candidate.user.pk)


post_init.connect(message_post_init, Message)

from django.db import models
from picklefield.fields import PickledObjectField


from beta_invite.models import User, Campaign, EmailType
from dashboard.models import Candidate


class EmailSent(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.DO_NOTHING, null=True)
    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, user={1}, campaign={2}, email_type={3}'.format(self.pk, self.user, self.campaign, self.email_type)

    # adds custom table name
    class Meta:
        db_table = 'emails_sent'


class PendingEmail(models.Model):

    candidates = models.ManyToManyField(Candidate)
    language_code = models.CharField(max_length=3)
    body_input = models.CharField(max_length=10000)
    subject = models.CharField(max_length=200)
    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)

    # optional
    with_localization = models.BooleanField(default=True)
    body_is_filename = models.BooleanField(default=True)
    override_dict = PickledObjectField(default={})

    # internal
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}'.format(self.pk)

    @staticmethod
    def add_to_queue(**kwargs):

        candidates = kwargs.pop('candidates', None)

        email = PendingEmail(**kwargs)
        email.save()
        email.save_candidates(candidates)

    def save_candidates(self, candidates):
        """
        Can __init__ with 1 candidate or a list  of candidates.
        :param candidates:
        :return:
        """
        if candidates and type(candidates) != list:
            candidates = [candidates]

        self.candidates = candidates
        self.save()

    # adds custom table name
    class Meta:
        db_table = 'pending_emails'

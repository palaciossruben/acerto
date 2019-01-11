from django.db import models
from picklefield.fields import PickledObjectField


from beta_invite.models import EmailType, Campaign
from business.models import BusinessUser
from dashboard.models import Candidate


class CandidateEmailSent(models.Model):

    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)
    an_object = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, candidate_id={1}, email_type={2}'.format(self.pk, self.an_object.id, self.email_type)

    # adds custom table name
    class Meta:
        db_table = 'candidate_emails_sent'


class BusinessUserEmailSent(models.Model):

    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)
    an_object = models.ForeignKey(BusinessUser, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, candidate_id={1}, email_type={2}'.format(self.pk, self.an_object.id, self.email_type)

    # adds custom table name
    class Meta:
        db_table = 'business_user_emails_sent'


class CampaignEmailSent(models.Model):

    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)
    an_object = models.ForeignKey(Campaign, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, candidate_id={1}, email_type={2}'.format(self.pk, self.an_object.id, self.email_type)

    # adds custom table name
    class Meta:
        db_table = 'campaign_emails_sent'


# -------------------------------------------------------------------------------------------------------------------- #


class CandidatePendingEmail(models.Model):

    the_objects = models.ManyToManyField(Candidate)
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
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}'.format(self.pk)

    @staticmethod
    def add_to_queue(**kwargs):

        candidates = kwargs.pop('the_objects', None)

        email = CandidatePendingEmail(**kwargs)
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

        self.the_objects = candidates
        self.save()

    # adds custom table name
    class Meta:
        db_table = 'candidate_pending_emails'


class BusinessUserPendingEmail(models.Model):

    the_objects = models.ManyToManyField(BusinessUser)
    language_code = models.CharField(max_length=3)
    body_input = models.CharField(max_length=10000)
    subject = models.CharField(max_length=200)
    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING, null=True)

    # optional
    with_localization = models.BooleanField(default=True)
    body_is_filename = models.BooleanField(default=True)
    override_dict = PickledObjectField(default={})

    # internal
    sent = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}'.format(self.pk)

    @staticmethod
    def add_to_queue(**kwargs):

        business_users = kwargs.pop('the_objects', None)

        email = BusinessUserPendingEmail(**kwargs)
        email.save()
        email.save_business_users(business_users)

    def save_business_users(self, business_users):
        """
        Can __init__ with 1 business_user or a list of business_users.
        :param business_users:
        :return:
        """
        if business_users and type(business_users) != list:
            business_users = [business_users]

        self.the_objects = business_users
        self.save()

    # adds custom table name
    class Meta:
        db_table = 'business_user_pending_emails'


class CampaignPendingEmail(models.Model):

    the_objects = models.ManyToManyField(Campaign)
    language_code = models.CharField(max_length=3)
    body_input = models.CharField(max_length=10000)
    subject = models.CharField(max_length=200)
    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING, null=True)

    # optional
    with_localization = models.BooleanField(default=True)
    body_is_filename = models.BooleanField(default=True)
    override_dict = PickledObjectField(default={})

    # internal
    sent = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}'.format(self.pk)

    @staticmethod
    def add_to_queue(**kwargs):

        campaigns = kwargs.pop('the_objects', None)

        email = CampaignPendingEmail(**kwargs)
        email.save()
        email.save_campaigns(campaigns)

    def save_campaigns(self, campaigns):
        """
        Can __init__ with 1 campaign or a list of campaigns.
        :param campaigns:
        :return:
        """
        if campaigns and type(campaigns) != list:
            campaigns = [campaigns]

        self.the_objects = campaigns
        self.save()

    # adds custom table name
    class Meta:
        db_table = 'campaign_pending_emails'

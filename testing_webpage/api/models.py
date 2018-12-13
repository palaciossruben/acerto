import os
import basic_common
from django.db import models
from django.db.models.signals import post_init

from beta_invite.models import Campaign


class PublicPost(models.Model):
    """
    This table stores public messages sent later on, is a kind of queue
    """

    campaign = models.ForeignKey(Campaign)
    text = models.CharField(max_length=10000)
    sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'public_posts'

    def add_format_and_mark_as_sent(self):

        self.sent = True
        params = {'campaign_url': self.campaign.get_url(),
                  'title': self.campaign.title_es}
        self.text = self.text.format(**params)
        self.save()

        return self

    @staticmethod
    def add_to_public_post_queue(campaign):
        """
        Adds objects to the message table. So later on this table will serve as a message queue.
        :param campaign: a campaign.
        :return: writes on table messages to be sent.
        """
        # TODO: add English support
        with open(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_posts'), 'publication_es.txt'), 'r') as f:
            PublicPost(campaign=campaign, text=f.read()).save()


class Lead(models.Model):

    name = models.CharField(max_length=200, default='')
    phone = models.CharField(max_length=40, null=True)
    email = models.CharField(max_length=200, null=True)
    facebook_url = models.CharField(max_length=300, null=True)
    # messenger variables
    added = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}, {2}'.format(self.pk, self.name, self.phone)

    # adds custom table name
    class Meta:
        db_table = 'leads'

    @staticmethod
    def create_leads(names, phones, emails, facebook_urls):
        leads = []
        for n, p, e, f in zip(names, phones, emails, facebook_urls):
            if f not in [l.facebook_url for l in Lead.objects.all()]:
                l = Lead(name=n, phone=p, email=e, facebook_url=f)
                l.save()
                leads.append(l)

        return leads

    # TODO: have leads for different countries
    def get_calling_code(self):
        return '57'

    def change_to_international_phone_number(self, add_plus=False):
        self.phone = basic_common.change_to_international_phone_number(self.phone,
                                                                       self.get_calling_code(),
                                                                       add_plus=add_plus)
        return self.phone


class LeadMessage(models.Model):
    """
    This table stores messages sent later on. is a kind of queue, but for business leads
    """
    lead = models.ForeignKey(Lead)
    text = models.CharField(max_length=10000, default='')
    contact_name = models.CharField(max_length=200, default='')

    sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, {1}'.format(self.pk, self.text)

    # adds custom table name
    class Meta:
        db_table = 'lead_messages'

    def add_format_and_mark_as_sent(self, params):
        """
        Adds format to message and returns itself
        :return: self
        """
        self.text = self.text.format(**params)
        self.sent = True
        self.save()
        return self

    @staticmethod
    def add_to_message_queue(leads, messages):
        """
        Adds objects to the message table. So later on this table will serve as a message queue.
        :param leads: list of leads.
        :param messages: list of strings
        :return: writes on table messages to be sent.
        """
        for lead, message in zip(leads, messages):
            LeadMessage(lead=lead, text=message).save()

    @staticmethod
    def mark_as_added(leads):
        """
        Flag added to True value.
        :param leads: collection
        :return: none
        """
        for l in leads:
            l.added = True
            l.save()


def message_post_init(**kwargs):
    instance = kwargs.get('instance')
    instance.contact_name = instance.lead.name + ' ' + str(instance.lead.pk)


post_init.connect(message_post_init, LeadMessage)

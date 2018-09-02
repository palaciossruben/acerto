import os
from django.db import models

from beta_invite.util import common_senders
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
        with open(os.path.join(common_senders.get_public_post_path(), 'publication_es.txt'), 'r') as f:
            PublicPost(campaign=campaign, text=f.read()).save()

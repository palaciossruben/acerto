from django.db import models

from beta_invite.models import User, Campaign, EmailType
from dashboard.models import Candidate


class EmailSent(models.Model):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    campaign = models.ForeignKey(Campaign, on_delete=models.DO_NOTHING)
    email_type = models.ForeignKey(EmailType, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'id={0}, user={1}, campaign={2}, email_type={3}'.format(self.id, self.user, self.campaign, self.email_type)

    # adds custom table name
    class Meta:
        db_table = 'emails_sent'


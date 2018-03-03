from django import template
from business.models import BusinessUser

register = template.Library()


@register.filter
def get_campaign_url(campaign):
    return campaign.get_url()

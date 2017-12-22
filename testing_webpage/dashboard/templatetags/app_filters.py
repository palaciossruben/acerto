from django import template

register = template.Library()


@register.filter
def get_campaign_url(campaign):
    return campaign.get_url()

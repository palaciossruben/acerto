from django import template
from business.models import BusinessUser

register = template.Library()


@register.filter
def get_campaign_url(campaign):
    return campaign.get_url()


@register.filter
def get_dashboard_campaign_url(campaign):
        query = BusinessUser.objects.filter(campaigns__id__contains=campaign.pk)
        user = [id for id in query][0]
        return campaign.get_host()+'/servicio_de_empleo/tablero_de_control/{user_id}?campaign_id={campaign_id}'.format(user_id=user.id, campaign_id=campaign.pk)

import json
from django import template
from business.models import BusinessUser
from django.core.serializers import serialize
from django.db.models.query import QuerySet

register = template.Library()


@register.filter
def get_campaign_url(campaign):
    return campaign.get_url()

'''
@register.filter
def get_dashboard_campaign_url(campaign):
        query = BusinessUser.objects.filter(campaigns__id__in=[campaign.pk])
        user = [id for id in query][0]
        return campaign.get_host()+'/seleccion_de_personal/candidatos/{user_id}?campaign_id={campaign_id}'.format(user_id=user.id, campaign_id=campaign.pk)
'''


@register.filter
def get_business_user_id_from_auth_user(user):
    return BusinessUser.objects.get(auth_user=user).pk


@register.filter
def jsonify(my_object):
    return serialize('json', my_object)


@register.filter
def dict_get(d, key):
    return d.get(str(key))


@register.filter
def print_score(score):
    if score is not None:
        return str(round(score)) + '%'
    else:
        return ''


@register.filter
def int_rounding(score):
    if score is not None:
        return round(score)
    else:
        return 0

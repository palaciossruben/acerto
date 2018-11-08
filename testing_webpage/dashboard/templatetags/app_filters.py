from django import template
from business.models import BusinessUser
from django.core.serializers import serialize
import common
register = template.Library()


@register.filter
def get_campaign_url(campaign):
    return campaign.get_url()


@register.filter
def get_dashboard_campaign_url(campaign):
        query = BusinessUser.objects.filter(campaigns__id__in=[campaign.pk])
        user = [id for id in query][0]
        return campaign.get_host()+'/seleccion_de_personal/candidatos/{user_id}?campaign_id={campaign_id}'.format(user_id=user.id, campaign_id=campaign.pk)


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
    if score is not None and isinstance(score, float):
        return round(score)
    else:
        return 0


@register.filter
def get_business_user_name_with_campaign(campaign):
    return common.get_business_user_with_campaign(campaign, 'name')


@register.filter
def get_business_user_company_with_campaign(campaign):
    return common.get_business_user_with_campaign(campaign, 'company')


@register.filter
def get_number_questions_of_before_test(tests, i):
    if int(i) < 1:
        return len(tests[0].questions.all())
    # the -2 is for an index based of 1 not in zero
    return len(tests[int(i)-2].questions.all())

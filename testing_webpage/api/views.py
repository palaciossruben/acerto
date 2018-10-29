from api.models import PublicPost
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from api.models import LeadMessage, Lead
from ipware.ip import get_ip

from beta_invite.models import City, WorkArea
from beta_invite import new_user_module
import common


def get_public_posts(request):
    """
    Sends the messages and their respective users.
    :param request: HTTP
    :return: json
    """

    posts = [m.add_format_and_mark_as_sent() for m in PublicPost.objects.filter(sent=False)]

    posts_json = serializers.serialize('json', posts)

    return JsonResponse(posts_json, safe=False)


def add_messages(request):

    # TODO: Change from GET to POST
    messages = request.GET.getlist('messages')
    facebook_urls = request.GET.getlist('facebook_urls')

    if facebook_urls is not None and messages is not None:
        LeadMessage.add_to_message_queue(Lead.objects.filter(facebook_url__in=facebook_urls), messages)
        return HttpResponse('<h1>Oki doki</h1>', status=200)
    else:
        error_message = '<h1>The request misses crucial information (names, messages, phones or emails)</h1>'
        return HttpResponse(error_message, status=400)


def save_leads(request):

    # TODO: Change from GET to POST
    names = request.GET.getlist('names')
    phones = request.GET.getlist('phones')
    emails = request.GET.getlist('emails')
    facebook_urls = request.GET.getlist('facebook_urls')

    if names is not None and phones is not None and emails is not None:
        new_leads = Lead.create_leads(names, phones, emails, facebook_urls)
        return JsonResponse([l.facebook_url for l in new_leads], status=200)
    else:
        error_message = '<h1>The request misses crucial information (names, messages, phones or emails)</h1>'
        return HttpResponse(error_message, status=400)


@csrf_exempt
def register(request):
    """
    type=POST
    end point: peaku.co/api/v1/register

    optional params:
        email = str
        name = str
        phone = str
        work_area_id = int
        city_id = int
        google_token = str
        politics = str
        campaign_id = int

    optional FILES:
        curriculum_url
        photo_url
        brochure_url

    :param request: HTTP
    :return: 201=created, 200=updated, 400=missing google token
    """

    email = request.POST.get('email')
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    work_area_id = request.POST.get('work_area_id')
    city_id = request.POST.get('city_id')
    google_token = request.POST.get('google_token')
    politics = True if request.POST.get('politics') else False

    if not google_token:
        return HttpResponse(400)

    campaign = common.get_campaign_from_request(request)
    country = common.get_country_with_request(request)

    user_params = {'country': country,
                   'ip': get_ip(request),
                   'is_mobile': True,
                   'language_code': request.LANGUAGE_CODE
                   }

    if name:
        user_params['name'] = name

    if email:
        user_params['email'] = email

    if email:
        user_params['phone'] = phone

    if work_area_id:
        user_params['phone'] = work_area_id

    if city_id:
        user_params['city'] = City.objects.get(pk=city_id)

    if politics:
        user_params['politics'] = politics

    user = new_user_module.user_if_exists(email, phone, campaign)
    if user:
        new_user_module.update_user(campaign, user, user_params, request)
        return HttpResponse(200)
    else:
        new_user_module.create_user(campaign, user_params, request, is_mobile=True)
        return HttpResponse(201)


@csrf_exempt
def get_work_areas(request):
    """
    type=GET
    end point: peaku.co/api/v1/get_work_areas

    optional params:
        None
    optional FILES:
        None

    :param request: HTTP
    :return: Work Area json:
        {
          "model":"beta_invite.workarea",
          "pk":1,
          "fields":{
             "name":"Administraciu00f3n  Oficina",
             "name_es":"Administraciu00f3n  Oficina",
             "segment":1,
             "code":"AO"
          }
       },
    """
    my_json = serializers.serialize('json', WorkArea.objects.all())
    return JsonResponse(my_json, safe=False)


@csrf_exempt
def get_cities(request):
    """
    type=GET
    end point: peaku.co/api/v1/get_cities

    optional params:
        None
    optional FILES:
        None

    :param request: HTTP
    :return: City json:
    {
      "model":"beta_invite.city",
      "pk":1,
      "fields":{
         "name":"Chennai",
         "country":null
      }
    },
    """
    my_json = serializers.serialize('json', City.objects.all())
    return JsonResponse(my_json, safe=False)

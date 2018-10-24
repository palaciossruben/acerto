from api.models import PublicPost
from django.core import serializers
from django.http import JsonResponse
from django.http import HttpResponse

from api.models import LeadMessage, Lead


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

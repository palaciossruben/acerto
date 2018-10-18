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
    names = request.GET.getlist('names')
    messages = request.GET.getlist('messages')
    phones = request.GET.getlist('phones')
    emails = request.GET.getlist('emails')

    if names is not None and messages is not None and phones is not None and emails is not None:
        LeadMessage.add_to_message_queue(Lead.create_leads(names, phones, emails), messages)
        return HttpResponse('<h1>Oki doki</h1>', status=200)
    else:
        error_message = '<h1>The request misses crucial information (names, messages, phones or emails)</h1>'
        return HttpResponse(error_message,
                            status=400)

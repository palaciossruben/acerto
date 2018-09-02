from api.models import PublicPost
from django.core import serializers
from django.http import JsonResponse


def get_public_posts(request):
    """
    Sends the messages and their respective users.
    :param request: HTTP
    :return: json
    """

    posts = [m.add_format_and_mark_as_sent() for m in PublicPost.objects.filter(sent=False)]

    posts_json = serializers.serialize('json', posts)

    return JsonResponse(posts_json, safe=False)

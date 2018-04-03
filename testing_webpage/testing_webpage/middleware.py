from django.utils import translation
import common


class ForceLangMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        language = common.get_language_with_ip(request)

        translation.activate(language)
        request.LANGUAGE_CODE = language

        return request

    def process_response(self, request, response):

        translation.deactivate()
        return response

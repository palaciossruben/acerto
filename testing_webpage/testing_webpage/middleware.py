from ipware.ip import get_ip
from django.utils import translation

# from django.contrib.gis.geoip import GeoIP


class ForceLangMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):

        # TODO: now it is defaulting to 'es', it should work with ip's by country.
        #language = translation.get_language_from_request(request)
        # g = GeoIP()
        # g.country('google.com')
        # ip = get_ip(request)
        language = 'es'
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        return request

    def process_response(self, request, response):
        translation.deactivate()
        return response

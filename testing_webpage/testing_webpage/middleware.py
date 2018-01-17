from ipware.ip import get_ip
from django.conf import settings
from django.utils import translation

from django.contrib.gis.geoip import GeoIP


class ForceLangMiddleware:

    def __init__(self, get_response):
        pass
        self.get_response = get_response

    def __call__(self, request):
        request = self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):

        #g = GeoIP()
        #g.country('google.com')

        #ip = get_ip(request)

        request.LANGUAGE_CODE = 'es'
        request.LANG = 'es'
        return request

        """
        request.LANG = getattr(settings, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        translation.activate(request.LANG)
        request.LANGUAGE_CODE = request.LANG"""

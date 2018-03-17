from ipware.ip import get_ip
from django.utils import translation

from django.contrib.gis.geoip import GeoIP

from beta_invite.models import Country


class ForceLangMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):

        # TODO: now it is defaulting to 'es', it should work with ip's by country.
        #language = translation.get_language_from_request(request)
        #g = GeoIP()
        #g.country('google.com')
        ip = get_ip(request)

        #from geoip import geolite2
        #match = geolite2.lookup('17.0.0.1')
        #country = Country.objects.get(ISO=match)

        #from geolite2 import geolite2

        #reader = geolite2.reader()
        #country = reader.get('172.19.26.137')
        #country = reader.get('1.1.1.1')

        #country = False

        #geolite2.close()

        import re
        import json
        import requests

        url = 'http://ipinfo.io/json'
        response = requests.get(url)

        #city = response['city']
        #country = response['country']
        country = None

        if country:
            language = country.language_code
        else:
            language = 'en'

        #language = 'es'
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        return request

    def process_response(self, request, response):
        translation.deactivate()
        return response

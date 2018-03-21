from django.apps import AppConfig
import geoip2.database
import os


class BetaInviteConfig(AppConfig):
    name = 'beta_invite'

    def ready(self):
        # Singleton utility
        # We load them here to avoid multiple instantiation across other
        # modules, that would take too much time.

        base_path = os.path.realpath(__file__).replace('apps.py', '..')

        print("Loading ip_country_reader...")
        country_path = os.path.join(base_path, os.path.join('GeoLite2-Country_20180306', 'GeoLite2-Country.mmdb'))
        global ip_country_reader
        ip_country_reader = geoip2.database.Reader(country_path)
        print("done loading ip_country_reader!")

        print("Loading ip_city_reader...")
        city_path = os.path.join(base_path, os.path.join('GeoLite2-City_20180306', 'GeoLite2-City.mmdb'))
        global ip_city_reader
        ip_city_reader = geoip2.database.Reader(city_path)
        print("done loading ip_city_reader!")

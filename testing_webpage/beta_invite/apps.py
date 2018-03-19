from django.apps import AppConfig
import geoip2.database


class BetaInviteConfig(AppConfig):
    name = 'beta_invite'

    def ready(self):
        # Singleton utility
        # We load them here to avoid multiple instantiation across other
        # modules, that would take too much time.
        print("Loading ip_country_reader...")
        global ip_country_reader
        ip_country_reader = geoip2.database.Reader('GeoLite2-Country_20180306/GeoLite2-Country.mmdb')
        print("done loading ip_country_reader!")

        print("Loading ip_city_reader...")
        global ip_city_reader
        ip_city_reader = geoip2.database.Reader('GeoLite2-City_20180306/GeoLite2-City.mmdb')
        print("done loading ip_city_reader!")

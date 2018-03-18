from django.apps import AppConfig
import geoip2.database


class BetaInviteConfig(AppConfig):
    name = 'beta_invite'

    def ready(self):
        # Singleton utility
        # We load them here to avoid multiple instantiation across other
        # modules, that would take too much time.
        print("Loading ip reader...")
        global ip_country_reader
        ip_country_reader = geoip2.database.Reader('GeoLite2-Country_20180306/GeoLite2-Country.mmdb')
        print("done loading ip reader!")

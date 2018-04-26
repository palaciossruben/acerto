import raven
from testing_webpage.shared_settings import *
from decouple import config

print('using production settings')

ABSOLUTE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# HTTPS only!
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Adds Sentry only on production
RAVEN_CONFIG = {
    'dsn': config('sentry_dsn'),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.path.dirname(ABSOLUTE_DIR))),
}
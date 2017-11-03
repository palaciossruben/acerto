from testing_webpage.shared_settings import *

print('using production settings')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# HTTPS only!
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

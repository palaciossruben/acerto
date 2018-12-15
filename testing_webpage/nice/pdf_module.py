"""
For this to work you have to install pdfkit and wkhtmltopdf see:
https://github.com/JazzCore/python-pdfkit

VERY IMPORTANT:
IN LINUX a bug had to be solved by patching the pdfkit library:
Had to install xvfb:
sudo apt-get install xvfb

And then add 'xvfb-run' infront of the wkhtmltopdf command inside the library done by adding:
        yield 'xvfb-run'
in line 83 of pdfkit.py internal library...
see:
https://unix.stackexchange.com/questions/192642/wkhtmltopdf-qxcbconnection-could-not-connect-to-display/223694#223694
"""

import os
import sys
import platform
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
dir_separator = '\\' if 'Windows' == platform.system() else '/'
# how deep is this file from the project working directory?
dir_depth = 1
path_to_add = dir_separator.join(os.getcwd().split(dir_separator)[:-dir_depth])
sys.path.insert(0, path_to_add)

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import pdfkit
import urllib.parse
from django.db.models import Q

from testing_webpage import settings
from dashboard.models import Candidate
from decouple import config
from raven import Client

SENTRY_CLIENT = Client(config('sentry_dsn'))


def render_cv(candidate_id):
    filename = 'cv_{}.pdf'.format(candidate_id)
    base_url = 'http://127.0.0.1:8000' if settings.DEBUG else 'https://peaku.co'
    file_path = os.path.join('.', 'cv', filename)

    content_url = urllib.parse.urljoin(base_url, 'cv/{}'.format(candidate_id))
    pdfkit.from_url(content_url, file_path)


if __name__ == '__main__':

    for c in Candidate.objects.filter(~Q(user__experiences=None), render_cv=False):
        try:
            render_cv(c.id)
            c.render_cv = True
            c.save()
        except:
            SENTRY_CLIENT.captureException()

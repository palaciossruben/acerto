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
import pdfkit
import urllib.parse
from testing_webpage import settings
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Candidate
from django.views.decorators.csrf import csrf_exempt

from nice.cts import *
from nice import pdf_module


def cv_test(request, candidate_id):
    candidate = Candidate.objects.get(pk=candidate_id)
    return render(request, ELON_CV, {'candidate': candidate})


@csrf_exempt
def download_cv(request, candidate_id):
    #base_url = 'http://127.0.0.1:8000' if settings.DEBUG else 'https://peaku.co'
    filename = 'cv_{}.pdf'.format(candidate_id)
    #file_path = os.path.join('./nice', 'cv', filename)
    file_path = 'cv.pdf'

    #content_url = urllib.parse.urljoin(base_url, 'seleccion-de-personal/perfil-del-candidato/{}'.format(candidate_id))
    #content_url = urllib.parse.urljoin(base_url, 'cv/{}'.format(candidate_id))
    #print(content_url)
    #print(file_path)

    #pdfkit.from_url(content_url, file_path)
    #return HttpResponse(200)
    #pdf_module.render_cv(candidate_id, path_to_cv='nice/cv')

    candidate = Candidate.objects.get(pk=candidate_id)

    print(os.getcwd())

    #template = get_template(os.path.join('.', 'nice', 'templates', 'nice', 'elon_cv.html'))

    #template_path = '/Users/juanpabloisaza/Desktop/masteringmymind/acerto/API/testing_webpage/nice/templates/nice/elon_cv.html'
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/nice/elon_cv.html')
    print(template_path)
    template = get_template(template_path)
    html = template.render({'candidate': candidate})  # Renders the template with the context data.
    pdfkit.from_string(html, file_path)

    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        os.remove(file_path)
        return response
    except FileNotFoundError:
        return HttpResponse('Cannot find CV', status=404)

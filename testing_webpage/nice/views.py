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
from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Candidate
from django.views.decorators.csrf import csrf_exempt
from testing_webpage import settings
from nice.cts import *


def cv_test(request, candidate_id):
    candidate = Candidate.objects.get(pk=candidate_id)
    return render(request, ELON_CV, {'candidate': candidate})


@csrf_exempt
def download_cv(request, candidate_id):

    candidate = Candidate.objects.get(pk=candidate_id)
    filename = '{}_CV.pdf'.format(candidate.user.name)
    tmp_pdf = 'cv_tmp.pdf'
    nice_dir = os.path.dirname(os.path.realpath(__file__))

    template_path = os.path.join(nice_dir, 'templates', 'nice', 'elon_cv.html')
    template = get_template(template_path)
    html = template.render({'candidate': candidate})  # Renders the template with the context data.

    #css = os.path.join(nice_dir, 'static', 'nice', 'css', 'cv.css')
    pdfkit.from_string(html, tmp_pdf, css=css)
    #pdfkit.from_string(html, tmp_pdf)

    try:
        with open(tmp_pdf, 'rb') as f:
            response = HttpResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        os.remove(tmp_pdf)
        return response
    except FileNotFoundError:
        return HttpResponse('Cannot find CV', status=404)

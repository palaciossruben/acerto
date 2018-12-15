import os
import pdfkit
import urllib.parse
from testing_webpage import settings
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Candidate

from nice.cts import *


def cv_test(request, candidate_id):
    candidate = Candidate.objects.get(pk=candidate_id)
    return render(request, ELON_CV, {'candidate': candidate})


def download_cv(request, candidate_id):

    base_url = 'http://127.0.0.1:8000' if settings.DEBUG else 'https://peaku.co'
    filename = 'cv_{}.pdf'.format(candidate_id)
    file_path = os.path.join('./nice', 'cv', filename)
    #content_url = urllib.parse.urljoin(base_url, 'seleccion-de-personal/perfil-del-candidato/{}'.format(candidate_id))
    content_url = urllib.parse.urljoin(base_url, 'cv/{}'.format(candidate_id))
    print(content_url)

    pdfkit.from_url(content_url, file_path)
    with open(file_path, 'rb') as f:
        response = HttpResponse(f, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response

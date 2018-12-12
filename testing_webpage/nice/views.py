from django.shortcuts import render
from nice.cts import *


def cv_test(request):
    return render(request, ELON_CV)

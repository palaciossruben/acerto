from django.shortcuts import render


def index(request):
    """
    :param request: can come with args "name" and "email", if not it will load the initial page.
    :return: renders a view.
    """
    return render(request, 'index.html', {})

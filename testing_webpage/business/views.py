from beta_invite import views as beta_views


def index(request):
    """
    will render and have the same view as /beta_invite except for message customization.
    """
    print('on business index method')
    return beta_views.inner_index(request, is_user_site=False)

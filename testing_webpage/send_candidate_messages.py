import os
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()
from beta_invite.util import messenger
from dashboard.models import Candidate


def candidates_filter(candidates):

    user_ids = set()
    filtered_candidates = list()

    for c in candidates:
        if c.user_id not in user_ids:
            user_ids.add(c.user_id)
            filtered_candidates.append(c)
    return filtered_candidates


def send_candidates_messages():

    #candidates = Candidate.objects.filter(~Q(user=None),
    #                                      ~Q(user__phone=None),
    #                                      user__gender_id=None).order_by('-user_id')  # [:100]

    message = """
    Hola {name}
    
    Tengo tu información por nuestra base de datos y te cuento que estamos buscando desarrolladores front end bilingues para Bogotá (salarios entre los 4-6 M) con conocimiento en Javascript. Si te interesa aplica acá:
        
    https://peaku.co/servicio-de-empleo/?campaign_id=561
    
    Si conoces a alguien que le interese estamos entregando un bono de 300k en Ktronix si el candidato es contratado. Solo tienes que pasarnos su contacto de whatsapp. 
    
    Gracias y quedo atento!
    
    Saludos
    Juan Pablo de PeakU
    """

    candidates = list(Candidate.objects.filter(user__pk=1929))

    print(len(candidates))

    messenger.send(objects=candidates,
                   language_code='es',
                   body_input=message,
                   body_is_filename=False)


if __name__ == '__main__':
    send_candidates_messages()

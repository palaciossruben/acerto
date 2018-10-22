"""
This is a daemon, that uploads Users to ES (elastic search)
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import time
import urllib.parse
import requests
from botocore.exceptions import EndpointConnectionError
from beta_invite.models import User
from decouple import config
from queue import Queue
from subscribe import helper


def get_user_dict(user):
    return {'pk': user.pk,
            'email': user.email,
            'name': helper.remove_accents_and_non_ascii(user.name),
            'experience': user.experience,
            'profession': user.profession_id,
            'education': user.education_id,
            'country': user.country_id,
            'city': user.city_id,
            'curriculum_text': helper.remove_accents_and_non_ascii(user.curriculum_text),
            'phone': user.phone,
            'programs': helper.remove_accents_and_non_ascii(user.programs),
            'work_area': user.work_area_id,
            'salary': user.salary,
            'address': helper.remove_accents_and_non_ascii(user.address),
            'neighborhood': helper.remove_accents_and_non_ascii(user.neighborhood),
            'languages': helper.remove_accents_and_non_ascii(user.languages),
            'phone2': user.phone2,
            'phone3': user.phone3,
            'profile': helper.remove_accents_and_non_ascii(user.profile),
            'dream_job': helper.remove_accents_and_non_ascii(user.dream_job),
            'hobbies': helper.remove_accents_and_non_ascii(user.hobbies),
            }


def upload_resource_to_es(user):

    try:

        print("Indexing: {} in elastic search".format(user))
        r = requests.put(urllib.parse.urljoin(config('elastic_search_host'), 'users/user/{}'.format(user.pk)),
                         json=get_user_dict(user))
        print(r.status_code, r.reason)

        # returns True only if its successful; either a created new user or an update
        return True if str(r.status_code)[0] == '2' else False
    except EndpointConnectionError:
        print('EndpointConnectionError with: {}'.format(user))
        print('daemon will continue...')
    except UnicodeEncodeError:
        print('UnicodeEncodeError with: {}, will skip...'.format(user))

    return False


def add_new_users(queue):
    """
    Users with
     1. missing a s3 url
     2. having a local resource
     3. text analysis already done
    :return:
    """
    users = User.objects.filter(uploaded_to_es=False).order_by('id').all()
    print('total new users, to add on ES: {}'.format(len(users)))
    [queue.put(u) for u in users]


# each worker does this job
def upload_users(users_queue, wait_time_workers):
    """
    Uploads a User to es, then waits some time, and repeats...
    :return:
    """
    user = users_queue.get()
    user.uploaded_to_es = upload_resource_to_es(user)
    user.save()
    time.sleep(wait_time_workers)


def upload_all():

    wait_time_workers = 10  # seconds
    wait_time_db = 60  # 1 minute
    users_queue = Queue()

    while True:
        add_new_users(users_queue)
        while not users_queue.qsize() == 0:
            upload_users(users_queue, wait_time_workers)

        time.sleep(wait_time_db)


def run():
    #f = open('es_daemon.log', 'a')
    upload_all()
    #f.close()


if __name__ == '__main__':
    run()

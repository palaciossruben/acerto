import os
import sys
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import boto3
import time
import pickle
import urllib.parse
from botocore.exceptions import EndpointConnectionError
from threading import Thread
from beta_invite.models import User
from decouple import config
from django.db.models import Q
from queue import Queue

from testing_webpage import settings


NUM_WORKERS = 3
WAITING_TIME_WORKERS = 1  # seconds
WAITING_TIME_DB = 60  # seconds
users_queue = Queue()
DEBUG = False


def load_object(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f, "rb")


# the actual upload
def upload_resource_to_s3(user):

    bucket = config('aws_s3_bucket')
    s3_key = user.curriculum_url

    session = boto3.session.Session(region_name='us-east-2',
                                    aws_access_key_id=config('aws_access_key'),
                                    aws_secret_access_key=config('aws_secret_access_key'))

    s3client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'))

    try:
        s3client.upload_file(get_local_path(user), bucket, s3_key)
        s3_url = get_s3_path(bucket, s3_key)

        print("Uploaded: {} to: {}".format(get_local_path(user), s3_url))

        return s3_url
    except FileNotFoundError:
        print('FileNotFoundError: {}'.format(get_local_path(user)))
        #print('Will remove the fake cv url')
        #user.curriculum_url = '#'
        #user.save()
        print('daemon will continue...')
        return '#'
    except EndpointConnectionError:
        print('EndpointConnectionError with: {}'.format(get_local_path(user)))
        print('daemon will continue...')
        return '#'


def add_new_users(queue):
    """
    Users with
     1. missing a s3 url
     2. having a local resource
     3. text analysis already done
    :return:
    """
    # tODO: make it more efficient by usinf the SQL LIMIT
    [queue.put(u) for u in User.objects.filter(~Q(curriculum_url='#') &
                                               Q(curriculum_s3_url='#') &
                                               ~Q(curriculum_text=None)).all()]
    return queue


def get_s3_path(bucket, s3_key):
    return urllib.parse.urljoin(config('s3_base_url'), bucket + '/' + s3_key)


def get_local_path(user):
    return os.path.join('../static', user.curriculum_url)


# each worker does this job
def upload_users_cv():
    """
    Uploads a User to s3, then waits some time, and repeats...
    :return:
    """

    while True:
        user = users_queue.get()
        if DEBUG:
            user.curriculum_s3_url = 'LE FINI'
        else:
            user.curriculum_s3_url = upload_resource_to_s3(user)
        user.save()
        time.sleep(WAITING_TIME_WORKERS)


def init_workers(num_workers=NUM_WORKERS):
    for _ in range(num_workers):
        t = Thread(target=upload_users_cv)
        t.daemon = True
        t.start()


if __name__ == '__main__':

    init_workers()

    while True:
        if users_queue.empty:
            users_queue = add_new_users(users_queue)
        time.sleep(WAITING_TIME_DB)

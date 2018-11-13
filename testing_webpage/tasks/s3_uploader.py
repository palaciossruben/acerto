"""
This is a daemon, that uploads CV to S3
"""

import os
import sys
from datetime import datetime
from django.core.wsgi import get_wsgi_application

# Environment can use the models as if inside the Django app
sys.path.insert(0, '/'.join(os.getcwd().split('/')[:-1]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import boto3
import time
import urllib.parse
from botocore.exceptions import EndpointConnectionError
from beta_invite.models import User
from decouple import config
from django.db.models import Q
from queue import Queue
from subscribe import helper as h


def cool_print(s):
    print(str(datetime.today()) + ': ' + s)


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

        cool_print("Uploaded: {} to: {}".format(get_local_path(user), s3_url))

        return s3_url
    except FileNotFoundError:
        cool_print('FileNotFoundError: {}'.format(get_local_path(user)))
        cool_print('daemon will continue...')
        return '#'
    except EndpointConnectionError:
        cool_print('EndpointConnectionError with: {}'.format(get_local_path(user)))
        cool_print('daemon will continue...')
        return '#'
    except UnicodeEncodeError:
        cool_print('UnicodeEncodeError with CV of user_id: {}'.format(user.id))
        cool_print('daemon will continue...')
        return '#'


def add_new_users(queue, created_since):
    """
    Users with
     1. missing a s3 url
     2. having a local resource
     3. text analysis already done
    :return:
    """
    users = User.objects.filter(~Q(curriculum_url='#') &
                                Q(curriculum_s3_url='#')).all()
    # Q(created_at__gt=created_since)).all()
    cool_print('total new users, to add on S3: {}'.format(len(users)))
    [queue.put(u) for u in users]

    created_since = created_since if len(users) == 0 else max({u.created_at for u in users})

    return created_since


def get_s3_path(bucket, s3_key):
    return urllib.parse.urljoin(config('s3_base_url'), bucket + '/' + s3_key)


def get_local_path(user):
    return os.path.join('../media', user.curriculum_url)


# each worker does this job
def upload_users(users_queue, wait_time_workers, debug):
    """
    Uploads a User to s3, then waits some time, and repeats...
    :return:
    """
    user = users_queue.get()
    if debug:
        user.curriculum_s3_url = 'LE FINI'
    else:
        user.curriculum_s3_url = upload_resource_to_s3(user)
    user.save()
    time.sleep(wait_time_workers)


def upload_all():

    wait_time_workers = 10  # seconds
    wait_time_db = 60  # 10 minutes
    debug = False
    users_queue = Queue()

    created_since = datetime(day=9, month=4, year=1948)

    while True:
        created_since = add_new_users(users_queue, created_since)
        while not users_queue.qsize() == 0:
            upload_users(users_queue, wait_time_workers, debug)

        time.sleep(wait_time_db)


def run():
    # with open('s3_uploader.log', 'a') as f:
    #    sys.stdout = h.Unbuffered(f)
    upload_all()


if __name__ == '__main__':
    run()

import os
import subprocess
from uuid import getnode as get_mac

import psycopg2 as pg

from home_fabric import run, cd, prefix


WORKING_PATH = '/home/ubuntu/acerto/testing_webpage'


def my_parent_path():
    return str(os.path.dirname(os.path.abspath(__file__)).rpartition('/')[0])


def sync_local(sync_media=False):
    """
    Synchronizes local machine with last backup from DB and media files
    Args:
        sync_media: Boolean indicating if the sync will be done only for the DB or the media files as well.
    Returns:
    """

    # BE CAREFUL: THIS IS THE ONLY COMMAND THAT RUNS ON THE SERVER ON THIS TASK!!!
    run('pg_dump -U dbadmin -p 5432 -h localhost maindb > db_backup.sql')

    safe_machines = (181219919357696, )
    local_cwd = '/Users/juanpabloisaza/Desktop/acerto/'
    aws_machine = 'ubuntu@ec2-52-38-133-146.us-west-2.compute.amazonaws.com:'

    # BACKUP PATHS:
    backup_remote = '/home/ubuntu/db_backup.sql'
    local_backup = '/Users/juanpabloisaza/Desktop/acerto/db_backup.sql'

    # MEDIA PATHS:
    media_remote = my_parent_path() + '/media/resumes'
    media_local = my_parent_path() + '/media'

    # PSQL
    abstract_local_psql = 'psql -U {user} -p 5432 -h localhost {db_option}'
    postgres_psql = abstract_local_psql.format(user='postgres', db_option='')
    dbadmin_psql = abstract_local_psql.format(user='dbadmin', db_option='-d maindb')

    # COPY db_backup file to local machine. THIS IS EXECUTED LOCALLY!!!
    backup_command = 'scp -i production_key.pem {aws}{from_path} {to_path}'.format(aws=aws_machine,
                                                                                   from_path=backup_remote,
                                                                                   to_path=local_backup)
    print('BACKUP COMMAND: ' + str(backup_command))
    backup_out = subprocess.check_output(backup_command, cwd=local_cwd, shell=True)
    print('BACKUP_COMMAND output: ' + str(backup_out))

    # once backup is local then update DB:

    # Strong validation to make sure it is done on a safe computer:
    if get_mac() in safe_machines:

        # DROP LOCAL DB: BE CAREFUL!!!
        drop_command = "{psql} -c \'DROP DATABASE maindb;\'".format(psql=postgres_psql)
        subprocess.call(drop_command, shell=True)

        # CREATE EMPTY DB on localhost.
        create_command = "{psql} -c \'CREATE DATABASE maindb;\'".format(psql=postgres_psql)
        subprocess.call(create_command, shell=True)

        # Grant rights to user
        grant_sql = "{psql} -c \'GRANT ALL PRIVILEGES ON DATABASE maindb to dbadmin;\'".format(psql=postgres_psql)
        subprocess.call(grant_sql, shell=True)

        # Fill in with data
        fill_sql = "{psql} -f {local_backup}".format(psql=dbadmin_psql, local_backup=local_backup)
        subprocess.call(fill_sql, shell=True)

        # get connected to the database
        maindb_connection = pg.connect("dbname=maindb user=dbadmin")
        curs = maindb_connection.cursor()

        # Update Sequences
        curs.execute("SELECT setval('business_user_id_seq', (SELECT max(id) from business_users))")
        curs.execute("SELECT setval('business_visitor_id_seq', (SELECT max(id) from business_visitor))")
        curs.execute("SELECT setval('auth_user_id_seq', (SELECT max(id) from auth_user))")
        curs.execute("SELECT setval('searches_id_seq', (SELECT max(id) from searches))")
        curs.execute("SELECT setval('beta_invite_visitor_id_seq', (SELECT max(id) from visitors))")
        curs.execute("SELECT setval('beta_invite_user_id_seq', (SELECT max(id) from users))")

        # Closes connection
        maindb_connection.close()

    else:
        raise Exception("WTF are you trying to do!!! Be careful not to erase production.")

    if sync_media:

        # Syncs media folder. Only rewrites new or updated files. Note the syntax to consider the ssh key.
        media_command = "rsync -au -i -e \"ssh -i production_key.pem\" ubuntu@ec2-52-38-133-146.us-west-2.compute.amazonaws.com:/home/ubuntu/acerto/testing_webpage/media/ /Users/juanpabloisaza/Desktop/masteringmymind/acerto/testing_webpage/media/"

        print('MEDIA COMMAND: ' + str(media_command))
        media_out = subprocess.check_output(media_command, cwd=local_cwd, shell=True)
        print('MEDIA_COMMAND output: ' + str(media_out))


def deploy():

    local_cwd = my_parent_path()

    # first uploads my local changes to the repo
    subprocess.check_output("git push origin master", cwd=local_cwd, shell=True)

    # Then creates or overwrites the backup db file ;)
    run('pg_dump -U dbadmin -p 5432 -h localhost maindb > db_backup.sql')

    with cd(WORKING_PATH):

        # download latest changes to repo.
        run('git pull origin master')

        with prefix("source /usr/local/bin/virtualenvwrapper.sh && workon myenv"):

            # update the cron jobs, in case it has changed.
            run('crontab cron.txt')

            # TODO: make pdfminer installation work!
            # install any missing python package
            #run('sudo pip3 install pipreqs')  # First install pipreqs if missing
            #run('PYENV_VERSION=3.5.2 pipreqs testing_webpage/../ --force')  # pipreqs updates requirements.txt

            #try:
            #    run('sudo pip3 install -r requirements.txt')  # install packages if missing
            #except:  # shitty pdfminer
            #    pass

            # collect static files, then restart nginx.
            run('python3 manage.py collectstatic -v0 --noinput')
            run('sudo /etc/init.d/nginx restart')

            # updates translations to spanish
            run('python3 manage.py compilemessages -l es')

            # stop gunicorn if it is running.
            o = run('[ -f {} ] && echo "Found" || echo "Not found"'.format(os.path.join(WORKING_PATH, 'gunicorn_pid')))
            if "Found" in o:
                run('kill $(cat gunicorn_pid)')

            # While down; migrate:
            run('python3 manage.py migrate')

            # reload fixtures: Will overwrite tables with DB fixtures.
            # beta_invite fixtures
            fixtures_dirs = ['beta_invite', 'business', 'dashboard']
            fixtures_dirs = [f + '/fixtures/*' for f in fixtures_dirs]

            for f in fixtures_dirs:
                run('python3 manage.py loaddata {}'.format(f))

            # Last step: start gunicorn as a deamon: that binds to a unix socket, from where nginx listens.
            run('PYENV_VERSION=3.5.2 gunicorn -c gunicorn_cfg.py testing_webpage.wsgi --bind=unix:/opt/peaku_co/run/gunicorn.sock')


def dev_update():
    """
    Have the dev machines up to date.
    """

    python_cmd = 'python3'
    local_cwd = my_parent_path()

    subprocess.check_output('{} manage.py migrate'.format(python_cmd), cwd=local_cwd, shell=True)

    # reload fixtures: Will overwrite tables with DB fixtures.
    # beta_invite fixtures
    fixtures_dirs = ['beta_invite', 'business', 'dashboard']
    fixtures_dirs = [f + '/fixtures/*' for f in fixtures_dirs]

    for f in fixtures_dirs:
        subprocess.check_output('{python_cmd} manage.py loaddata {f}'.format(python_cmd=python_cmd,
                                                                             f=f), cwd=local_cwd, shell=True)


deploy()

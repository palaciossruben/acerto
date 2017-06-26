import os

from fabric.api import run, env, prefix
from fabric.context_managers import cd

env.use_ssh_config = True
env.always_use_pty = False

# It needs to have last '/' to work with list_dir custom function.
WORKING_PATH = '/home/ubuntu/acerto/testing_webpage/'


def list_files():
    #with cd('acerto/testing_webpage'):
    #    run('ls')
    list_dir('Desktop/')


def list_dir(directory=None):
    directory = directory or env.cwd
    string = run("for i in %s*; do echo $i; done" % directory)
    files = string.replace("\r", "").split("\n")
    return files


def deploy():

    with cd(WORKING_PATH):
        with prefix(". /usr/local/bin/virtualenvwrapper.sh; workon myenv"):

            # download latest changes to repo.
            run('git pull origin master')

            # install any missing python package
            run('sudo pip3 install pipreqs')  # First install pipreqs if missing
            run('PYENV_VERSION=3.5.2 pipreqs testing_webpage/../ --force')  # pipreqs updates requirements.txt

            try:
                run('sudo pip3 install -r requirements.txt')  # install packages if missing
            except:  # shitty pdfminer
                pass

            # collect static files, then restart nginx.
            run('python3 manage.py collectstatic -v0 --noinput')
            run('sudo /etc/init.d/nginx restart')

            # updates translations to spanish
            run('python3 manage.py compilemessages -l es')

            # reload fixtures: Will overwrite tables with DB fixtures.
            # beta_invite fixtures
            fixtures = list_dir('beta_invite/fixtures/')
            for fixture_json in fixtures:
                run('python3 manage.py loaddata {}'.format(fixture_json))

            # stop gunicorn if it is running.
            if os.path.join(WORKING_PATH, 'gunicorn_pid') in list_dir(WORKING_PATH):
                run('kill $(cat gunicorn_pid)')

            # Last step: start gunicorn as a deamon.
            run('PYENV_VERSION=3.5.2 gunicorn -c gunicorn_cfg.py testing_webpage.wsgi')

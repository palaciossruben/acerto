#!/usr/bin/env bash
git pull origin master;
crontab cron.txt;
python3 manage.py collectstatic -v0 --noinput;
sudo /etc/init.d/nginx restart;
python3 manage.py compilemessages -l es;
[ -f gunicorn_pid ] && kill $(cat gunicorn_pid) && echo killed gunicorn_pid;
python3 manage.py migrate;
python3 manage.py loaddata beta_invite/fixtures/*;
python3 manage.py loaddata business/fixtures/*;
python3 manage.py loaddata dashboard/fixtures/*;
PYENV_VERSION=3.5.2 gunicorn -c gunicorn_cfg.py testing_webpage.wsgi --bind=unix:/opt/peaku_co/run/gunicorn.sock;
cd match && python3 update_data_structures.py;
python3 manage.py clear_cache;
#!/bin/sh

python manage.py collectstatic --noinput
python manage.py wait_for_db
python manage.py migrate
gunicorn --bind :8000 --workers 3 app.wsgi:application

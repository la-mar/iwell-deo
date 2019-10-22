#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "$DJANGO_SETTINGS_MODULE"
python manage.py makemigrations
python manage.py migrate
gunicorn home.wsgi -b 0.0.0.0:8000 --name=ops-website --statsd-host=localhost:8125 --statsd-prefix=service.app

exec "$@"

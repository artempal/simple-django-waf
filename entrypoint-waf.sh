#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python import.py

if [ "$HTTPS_ON_PROXY" = "True" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/mydomain.key -out certs/mydomain.crt -subj '/CN=localhost'
    https_param=True
fi

python manage.py configuration $HOSTNAME_APP $PROXY_PORT $https_param
python manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User; User.objects.create_superuser('root', 'root@example.com', '$DJANGO_ROOT_PASS')" | python manage.py shell

exec "$@"

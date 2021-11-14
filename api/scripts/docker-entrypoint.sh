#!/bin/sh
set -e

/usr/src/api/scripts/wait-for-postgres.sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

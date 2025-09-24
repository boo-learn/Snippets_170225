#!/bin/sh

python3 manage.py migrate
manage.py collectstatic --no-input --clear

exec "$@"
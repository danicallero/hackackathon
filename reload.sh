#!/bin/sh

git pull

python3 manage.py migrate

python3 manage.py collectstatic

gunicorn >> gunicorn.log &

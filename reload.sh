#!/bin/sh

# Cambios
git pull

# Preparativos
python3 manage.py migrate
python3 manage.py collectstatic --noinput

# Recarga
pkill gunicorn
gunicorn >> gunicorn.log &

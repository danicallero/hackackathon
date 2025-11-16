#!/bin/sh

# Cambios
git reset --hard
git pull

# Preparativos
python3 manage.py migrate
python3 manage.py collectstatic --noinput

# Recarga
pkill gunicorn
sleep 5
gunicorn >> gunicorn.log &

#!/bin/sh

# Cambios
git reset --hard
git pull

# Preparativos
python3 manage.py migrate
python3 manage.py collectstatic --noinput

# Recarga
kill $(cat gunicorn.pid)
sleep 1
gunicorn

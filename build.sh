#!/usr/bin/env bash
# Script de build para Render (o cualquier plataforma que lo permita
# como "Build Command"). No hace falta ejecutarlo a mano localmente.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

#!/bin/bash
# Vercel build step: install deps and collect static assets (served by WhiteNoise).
set -e

python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python src/manage.py collectstatic --noinput --clear

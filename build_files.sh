#!/bin/bash
# Vercel build step: install deps and collect static assets (served by WhiteNoise).
set -e

pip install -r requirements.txt
python src/manage.py collectstatic --noinput --clear

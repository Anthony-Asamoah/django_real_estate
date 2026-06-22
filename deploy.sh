#!/bin/bash
set -e

python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python src/manage.py migrate --noinput

python src/manage.py collectstatic --noinput --clear

mkdir -p staticfiles_build
if [ -d src/staticfiles ]; then
  cp -r src/staticfiles/. staticfiles_build/ 2>/dev/null || true
fi
echo "static assets are served from S3/CDN in this deployment" > staticfiles_build/.vercel-keep

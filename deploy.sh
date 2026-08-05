#!/bin/bash
set -e

python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install uv

# Dependencies are declared in pyproject.toml and pinned in uv.lock.
uv export --frozen --no-dev --no-emit-project --format requirements-txt -o /tmp/requirements.txt
pip install -r /tmp/requirements.txt

python src/manage.py migrate --noinput

# Idempotently create the superuser and seed currencies, pages, and testimonials.
# Safe to run on every deploy; does not drop/flush the DB.
python src/manage.py init_app

python src/manage.py collectstatic --noinput --clear

mkdir -p staticfiles_build
if [ -d src/staticfiles ]; then
  cp -r src/staticfiles/. staticfiles_build/ 2>/dev/null || true
fi
echo "static assets are served from S3/CDN in this deployment" > staticfiles_build/.vercel-keep

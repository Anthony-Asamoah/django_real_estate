#!/bin/bash
# Vercel build step: install deps and run collectstatic.
# In S3 mode collectstatic UPLOADS assets to the S3 static bucket (served via
# CDN), so there is no local output dir. We still create the dir named by
# vercel.json#distDir so the static-build step has an output to hand back.
set -e

python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python src/manage.py collectstatic --noinput --clear

# Satisfy @vercel/static-build's distDir requirement. In local-storage mode
# collectstatic writes to src/staticfiles; mirror it here so it is still served.
mkdir -p staticfiles_build
if [ -d src/staticfiles ]; then
  cp -r src/staticfiles/. staticfiles_build/ 2>/dev/null || true
fi

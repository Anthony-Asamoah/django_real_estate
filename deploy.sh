#!/bin/bash
set -e

curl -LsSf https://astral.sh/uv/install.sh | sh || {
  python -m venv /tmp/uv-bootstrap
  /tmp/uv-bootstrap/bin/pip install uv
  mkdir -p "$HOME/.local/bin"
  ln -sf /tmp/uv-bootstrap/bin/uv "$HOME/.local/bin/uv"
}
export PATH="$HOME/.local/bin:$PATH"

# Dependencies are declared in pyproject.toml and pinned in uv.lock.
uv sync --frozen --no-dev --python 3.13
. .venv/bin/activate

python --version

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

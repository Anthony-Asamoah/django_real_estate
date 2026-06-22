"""
WSGI config for real_estate project.

It exposes the WSGI callable as a module-level variable named ``application``.
``app`` is also exported because Vercel's Python runtime looks for a WSGI/ASGI
callable named ``app``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Ensure the Django project root (src/) is importable so ``config`` resolves
# regardless of the working directory Vercel imports this module from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Vercel entrypoint.
app = application

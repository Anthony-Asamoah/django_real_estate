# Django Real Estate

A real-estate website and CMS built on [Wagtail](https://wagtail.org/) and Django. Almost everything that renders on the public site — pages, sections, blocks, branding colors, currencies, copy — is editable from the Wagtail admin rather than hardcoded in templates.

## Features

- **Page-driven content** — Home, About, Services (index + detail), Projects (index + detail), and Contact pages, all managed as Wagtail pages with StreamField blocks (hero slideshows, CTA banners, service cards, process steps, and more).
- **Projects** — Listings managed as Wagtail snippets, with per-project pricing and admin-configurable currencies.
- **Inquiries** — Project and general inquiry forms with email notifications and an "unread" indicator in the admin dashboard.
- **Testimonials** — Customer testimonials surfaced across the site, with unread notifications in admin.
- **Employees / team** — Team member profiles.
- **Branding** — Site-wide branding settings, color presets, and color history configured via Wagtail settings.
- **Custom CMS login** — Branded admin login at `/cms/login/` with a live gradient background.
- **Email** — Pluggable provider: Django SMTP (Gmail) or [Resend](https://resend.com/).
- **reCAPTCHA v3** and **Google Maps** embeds, configured via environment variables.

## Tech stack

- Python 3.13+
- Django 4.2 (LTS)
- Wagtail 6.3
- PostgreSQL (via `psycopg2`)
- [uv](https://github.com/astral-sh/uv) for dependency and environment management
- [Pendulum](https://pendulum.eustace.io/) for date/time handling

## Prerequisites

- Python 3.13+
- PostgreSQL (running locally or reachable)
- [uv](https://github.com/astral-sh/uv) installed

## Setup

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Configure environment**

   The project uses [`python-decouple`](https://github.com/HBNetwork/python-decouple). Create a `.env` file at the repository root (next to `pyproject.toml`):

   ```dotenv
   # Core
   SECRET_KEY=change-me
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_NAME=real_estate
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432

   # Site / Wagtail
   SITE_NAME=Real Estate
   WAGTAILADMIN_BASE_URL=http://localhost:8000

   # Email — 'django_smtp' or 'resend'
   EMAIL_PROVIDER=django_smtp
   DEFAULT_FROM_EMAIL=noreply@example.com
   EMAIL_HOST_USER=
   EMAIL_HOST_PASSWORD=
   EMAIL_API_KEY=

   # reCAPTCHA v3 (optional)
   RECAPTCHA_SITE_KEY=
   RECAPTCHA_SECRET_KEY=

   # Google Maps (optional)
   MAPS_URL=
   MAPS_EMBED_URL=
   ```

3. **Create the database**

   Make sure a PostgreSQL database matching `DB_NAME` exists (or let the seed command create it for you — see below).

## Running

All commands run from the `src/` directory using `uv run`.

```bash
cd src
uv run python manage.py migrate
uv run python manage.py runserver
```

- Public site: http://localhost:8000/
- Wagtail admin: http://localhost:8000/cms/

## Seeding data

A management command drops/recreates the database, runs migrations, creates a superuser, and seeds currencies, employees, pages, projects, and testimonials in one shot:

```bash
cd src
uv run python manage.py reset_and_seed
```

Useful flags:

- `--skip-drop` — flush and reseed instead of dropping/recreating the database.
- `--superuser-username`, `--superuser-email`, `--superuser-password` — override the default superuser (`admin` / `admin@example.com` / `admin`).

> ⚠️ This is destructive — it drops the configured database. Use only in development.

## Project structure

```
src/
├── config/              # Django/Wagtail settings, URLs, WSGI/ASGI
├── domains/             # Domain apps
│   ├── pages/           # Wagtail page models, blocks, branding, testimonials
│   ├── projects/        # Projects, currencies
│   ├── inquiries/       # Project & general inquiry forms, email settings
│   ├── employees/       # Team members
│   └── accounts/        # Custom CMS login & auth
├── infrastructure/
│   ├── scripts/         # Management commands (reset_and_seed)
│   └── seeds/           # Seed data and assets
├── templates/           # HTML templates (blocks, pages, admin, emails, …)
├── static/              # CSS, JS, fonts, images
└── manage.py
```

## Notes

- Content, styling, sections, and blocks are intended to be controlled through the Wagtail admin.
- The default Django admin is disabled; administration is done entirely through Wagtail at `/cms/`.
</content>
</invoke>

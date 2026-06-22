import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Idempotently initialise a fresh database: create the superuser and seed '
        'currencies, pages, and testimonials. Does NOT drop, flush, or migrate the '
        'database, and skips employees and projects. Safe to run on every deploy.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--superuser-username',
            default=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
            help='Superuser username (env: DJANGO_SUPERUSER_USERNAME, default: admin)',
        )
        parser.add_argument(
            '--superuser-email',
            default=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
            help='Superuser email (env: DJANGO_SUPERUSER_EMAIL, default: admin@example.com)',
        )
        parser.add_argument(
            '--superuser-password',
            default=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin'),
            help='Superuser password (env: DJANGO_SUPERUSER_PASSWORD, default: admin)',
        )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        username = options['superuser_username']
        email = options['superuser_email']
        password = options['superuser_password']

        self.stdout.write(self.style.WARNING('Ensuring superuser exists...'))
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(f'  Created superuser: {username}')
            if password == 'admin':
                self.stdout.write(self.style.WARNING(
                    '  WARNING: using the default password "admin" — set '
                    'DJANGO_SUPERUSER_PASSWORD for production.'
                ))
        else:
            self.stdout.write(f'  Superuser "{username}" already exists — skipped.')

        from infrastructure.seeds.currencies import seed_currencies
        from infrastructure.seeds.pages import seed_pages
        from infrastructure.seeds.testimonials import seed_testimonials

        self.stdout.write(self.style.WARNING('Seeding data (idempotent)...'))
        self.stdout.write('  Seeding currencies...')
        seed_currencies()
        self.stdout.write('  Seeding pages...')
        seed_pages()
        self.stdout.write('  Seeding testimonials...')
        seed_testimonials()

        self.stdout.write(self.style.SUCCESS('\nDone! App initialised (employees and projects skipped).'))

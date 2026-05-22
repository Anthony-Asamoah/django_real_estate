import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Drop and recreate the database, run migrations, create superuser, and seed all data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--superuser-username',
            default='admin',
            help='Superuser username (default: admin)',
        )
        parser.add_argument(
            '--superuser-email',
            default='admin@example.com',
            help='Superuser email (default: admin@example.com)',
        )
        parser.add_argument(
            '--superuser-password',
            default='admin',
            help='Superuser password (default: admin)',
        )
        parser.add_argument(
            '--skip-drop',
            action='store_true',
            help='Skip dropping/recreating the DB — only flush, migrate, and seed.',
        )

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        db_name = db['NAME']
        db_user = db.get('USER', '')
        db_host = db.get('HOST', 'localhost')
        db_port = str(db.get('PORT', 5432))

        base_env = {
            'PGPASSWORD': db.get('PASSWORD', ''),
            'PATH': '/usr/local/bin:/usr/bin:/bin',
        }
        import os
        base_env.update(os.environ)

        pg_args = []
        if db_user:
            pg_args += ['-U', db_user]
        if db_host:
            pg_args += ['-h', db_host]
        if db_port:
            pg_args += ['-p', db_port]

        if not options['skip_drop']:
            self.stdout.write(self.style.WARNING(f'Terminating existing connections to "{db_name}"...'))
            terminate_sql = (
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
            )
            subprocess.run(
                ['psql'] + pg_args + ['-d', 'postgres', '-c', terminate_sql],
                env=base_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self.stdout.write(self.style.WARNING(f'Dropping database "{db_name}"...'))
            result = subprocess.run(
                ['dropdb', '--if-exists'] + pg_args + [db_name],
                env=base_env,
            )
            if result.returncode != 0:
                self.stderr.write(self.style.ERROR('dropdb failed — aborting.'))
                sys.exit(1)

            self.stdout.write(self.style.WARNING(f'Creating database "{db_name}"...'))
            result = subprocess.run(
                ['createdb'] + pg_args + [db_name],
                env=base_env,
            )
            if result.returncode != 0:
                self.stderr.write(self.style.ERROR('createdb failed — aborting.'))
                sys.exit(1)
        else:
            self.stdout.write('Skipping DB drop — flushing existing data...')
            call_command('flush', '--no-input')

        self.stdout.write(self.style.WARNING('Running migrations...'))
        call_command('migrate', '--no-input')

        self.stdout.write(self.style.WARNING('Creating superuser...'))
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = options['superuser_username']
        password = options['superuser_password']
        email = options['superuser_email']
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(f'  Created superuser: {username} / {password}')
        else:
            self.stdout.write(f'  Superuser "{username}" already exists — skipped.')

        self.stdout.write(self.style.WARNING('Seeding data...'))
        from infrastructure.seeds.employees import seed_employees
        from infrastructure.seeds.pages import seed_pages
        from infrastructure.seeds.projects import seed_projects
        from infrastructure.seeds.testimonials import seed_testimonials

        self.stdout.write('  Seeding employees...')
        seed_employees()
        self.stdout.write('  Seeding pages...')
        seed_pages()
        self.stdout.write('  Seeding projects...')
        seed_projects()
        self.stdout.write('  Seeding testimonials...')
        seed_testimonials()

        self.stdout.write(self.style.SUCCESS('\nDone! Fresh database seeded.'))
        self.stdout.write(f'  Admin login: {username} / {password}')

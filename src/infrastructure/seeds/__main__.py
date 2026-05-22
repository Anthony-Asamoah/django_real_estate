import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()


def run():
    from .currencies import seed_currencies
    from .employees import seed_employees
    from .projects import seed_projects
    from .testimonials import seed_testimonials
    from .pages import seed_pages

    print('Seeding currencies...')
    c = seed_currencies()

    print('Seeding employees...')
    e = seed_employees()

    print('Seeding projects...')
    pr = seed_projects()

    print('Seeding testimonials...')
    t = seed_testimonials()

    print('Seeding pages...')
    p = seed_pages()

    print(f'\nDone. Created {c} currency(ies), {e} employee(s), {pr} project(s), {t} testimonial(s), and {p} page(s).')


run()

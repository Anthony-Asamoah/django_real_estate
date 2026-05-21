import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()


def run():
    from .realtors import seed_realtors
    from .listings import seed_listings
    from .pages import seed_pages

    print('Seeding realtors...')
    r = seed_realtors()

    print('Seeding listings...')
    l = seed_listings()

    print('Seeding pages...')
    p = seed_pages()

    print(f'\nDone. Created {r} realtor(s), {l} listing(s), and {p} page(s).')


run()

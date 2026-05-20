import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()


def run():
    from .realtors import seed_realtors
    from .listings import seed_listings

    print('Seeding realtors...')
    r = seed_realtors()

    print('Seeding listings...')
    l = seed_listings()

    print(f'\nDone. Created {r} realtor(s) and {l} listing(s).')


run()

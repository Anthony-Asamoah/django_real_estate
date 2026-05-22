from pathlib import Path

import pendulum
from django.core.files import File

from domains.employees.models import Employee

MEDIA_DIR = Path(__file__).parent / 'assets'

EMPLOYEES = [
    {
        'name': 'Abena Mensah',
        'role': 'Senior Project Manager',
        'description': (
            'Abena has over 10 years of experience managing residential construction projects '
            'across the Upper East Region. She specialises in client relations and timely project delivery.'
        ),
        'email': 'abena@company.com',
        'phone': '+233 24 000 0101',
        'is_featured': True,
        'hire_date': pendulum.datetime(2015, 3, 12),
        'photo_file': 'jenny.jpg',
    },
    {
        'name': 'Kofi Asante',
        'role': 'Site Engineer',
        'description': (
            'Kofi brings 7 years of civil engineering expertise. '
            'He oversees infrastructure, borehole, and road projects on the ground.'
        ),
        'email': 'kofi@company.com',
        'phone': '+233 24 000 0202',
        'is_featured': False,
        'hire_date': pendulum.datetime(2018, 6, 20),
        'photo_file': 'mark.jpg',
    },
    {
        'name': 'Ama Boateng',
        'role': 'Business Development',
        'description': (
            'Ama focuses on client acquisition and high-value project portfolios. '
            'With 5 years in the industry, she has led some of the company\'s biggest contracts in the region.'
        ),
        'email': 'ama@company.com',
        'phone': '+233 24 000 0303',
        'is_featured': False,
        'hire_date': pendulum.datetime(2020, 1, 8),
        'photo_file': 'alex.jpg',
    },
]


def seed_employees():
    created = 0
    for data in EMPLOYEES:
        photo_file = data.pop('photo_file')
        obj, was_created = Employee.objects.get_or_create(
            email=data['email'],
            defaults=data,
        )
        if was_created:
            photo_path = MEDIA_DIR / 'images'/ photo_file
            if photo_path.exists():
                with open(photo_path, 'rb') as f:
                    obj.photo.save(photo_file, File(f), save=True)
            created += 1
            print(f'  Created employee: {obj.name}')
        else:
            print(f'  Skipped (exists): {obj.name}')
    return created

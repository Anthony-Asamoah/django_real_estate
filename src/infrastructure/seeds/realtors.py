import pendulum
from domains.realtors.models import realtor

REALTORS = [
    {
        'name': 'Jenny Doe',
        'description': (
            'Jenny has over 10 years of experience in residential real estate. '
            'She specializes in first-time buyers and relocation clients.'
        ),
        'email': 'jenny@btre.com',
        'phone': '617-555-0101',
        'is_mvp': True,
        'hire_date': pendulum.datetime(2015, 3, 12),
        'photo': 'media/2022/04/16/jenny.jpg',
    },
    {
        'name': 'Mark Spencer',
        'description': (
            'Mark brings 7 years of commercial and residential sales expertise. '
            'He is known for negotiating the best deals for his clients.'
        ),
        'email': 'mark@btre.com',
        'phone': '617-555-0202',
        'is_mvp': False,
        'hire_date': pendulum.datetime(2018, 6, 20),
        'photo': 'media/2022/04/16/mark.jpg',
    },
    {
        'name': 'Alex Rivera',
        'description': (
            'Alex focuses on luxury properties and investment portfolios. '
            'With 5 years in the industry, he has closed over $50M in sales.'
        ),
        'email': 'alex@btre.com',
        'phone': '617-555-0303',
        'is_mvp': False,
        'hire_date': pendulum.datetime(2020, 1, 8),
        'photo': 'media/2022/04/16/PicsArt_12-22-02.47.42.jpg',
    },
]


def seed_realtors():
    created = 0
    for data in REALTORS:
        obj, was_created = realtor.objects.get_or_create(
            email=data['email'],
            defaults=data,
        )
        if was_created:
            created += 1
            print(f'  Created realtor: {obj.name}')
        else:
            print(f'  Skipped (exists): {obj.name}')
    return created

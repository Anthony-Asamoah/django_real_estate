from domains.projects.models import Currency

CURRENCIES = [
    {'code': 'GHS', 'name': 'Ghanaian Cedi',     'symbol': 'GH₵'},
    {'code': 'USD', 'name': 'US Dollar',          'symbol': '$'},
    {'code': 'EUR', 'name': 'Euro',               'symbol': '€'},
    {'code': 'GBP', 'name': 'British Pound',      'symbol': '£'},
    {'code': 'NGN', 'name': 'Nigerian Naira',     'symbol': '₦'},
    {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R'},
]


def seed_currencies():
    created = 0
    for data in CURRENCIES:
        obj, was_created = Currency.objects.get_or_create(
            code=data['code'],
            defaults=data,
        )
        if was_created:
            created += 1
            print(f'  Created currency: {obj.code} — {obj.name}')
        else:
            print(f'  Skipped (exists): {obj.code}')
    return created

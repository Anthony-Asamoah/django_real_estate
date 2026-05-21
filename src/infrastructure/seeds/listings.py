import pendulum
from domains.listings.models import Listing
from domains.realtors.models import realtor

LISTINGS = [
    {
        'title': 'Beautiful Modern Home',
        'address': '22 Backbridge St',
        'city': 'Kensington',
        'state_or_region': 'MD',
        'zipcode': '20895',
        'description': (
            'A stunning modern home with open-plan living, high ceilings, '
            'and a chef\'s kitchen. Situated on a quiet tree-lined street.'
        ),
        'price': 675000,
        'bedrooms': 4,
        'bathrooms': 2.5,
        'garage': 2,
        'sqft': 2800,
        'lot_size': 0.5,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 19, 19, 26),
        'photo_main': 'media/2022/26/04/19/22/home-1.jpg',
        'photo_1': 'media/2022/26/04/19/22/home-2.jpg',
        'photo_2': 'media/2022/26/04/19/22/home-3.jpg',
        'photo_3': 'media/2022/26/04/19/22/home-4.jpg',
        'photo_4': 'media/2022/27/04/19/22/home-5.jpg',
        'photo_5': 'media/2022/27/04/19/22/home-6.jpg',
        'realtor_name': 'Jenny Doe',
    },
    {
        'title': 'Cozy Suburban Retreat',
        'address': '55 Oak Lane',
        'city': 'Rockville',
        'state_or_region': 'MD',
        'zipcode': '20850',
        'description': (
            'Charming 3-bedroom home with a spacious backyard, updated bathrooms, '
            'and a newly renovated kitchen perfect for family gatherings.'
        ),
        'price': 425000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'garage': 1,
        'sqft': 1950,
        'lot_size': 0.3,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 16, 16, 59),
        'photo_main': 'media/2022/59/04/16/22/home-1.jpg',
        'photo_1': 'media/2022/59/04/16/22/home-inside-1.jpg',
        'photo_2': 'media/2022/59/04/16/22/home-inside-2.jpg',
        'photo_3': 'media/2022/59/04/16/22/home-inside-3.jpg',
        'photo_4': 'media/2022/59/04/16/22/home-inside-4.jpg',
        'photo_5': 'media/2022/59/04/16/22/home-inside-5.jpg',
        'realtor_name': 'Mark Spencer',
    },
    {
        'title': 'Elegant Colonial Estate',
        'address': '101 Maple Drive',
        'city': 'Bethesda',
        'state_or_region': 'MD',
        'zipcode': '20814',
        'description': (
            'A grand colonial estate with 5 bedrooms, formal dining room, '
            'library, and beautifully landscaped grounds. A rare find.'
        ),
        'price': 950000,
        'bedrooms': 5,
        'bathrooms': 3.5,
        'garage': 3,
        'sqft': 4200,
        'lot_size': 1.2,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 16, 16, 8),
        'photo_main': 'media/2022/08/04/16/22/home-4.jpg',
        'photo_1': 'media/2022/04/16/home-inside-6.jpg',
        'realtor_name': 'Jenny Doe',
    },
    {
        'title': 'Downtown Luxury Condo',
        'address': '300 City View Blvd, Unit 12A',
        'city': 'Washington',
        'state_or_region': 'DC',
        'zipcode': '20001',
        'description': (
            'Sleek downtown condo with floor-to-ceiling windows, city views, '
            'rooftop pool, and concierge service. Walk to restaurants and metro.'
        ),
        'price': 520000,
        'bedrooms': 2,
        'bathrooms': 2.0,
        'garage': 1,
        'sqft': 1300,
        'lot_size': 0.0,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 16, 16, 10),
        'photo_main': 'media/2022/10/04/16/22/home-2.jpg',
        'realtor_name': 'Alex Rivera',
    },
    {
        'title': 'Spacious Family Home',
        'address': '78 Willow Creek Rd',
        'city': 'Silver Spring',
        'state_or_region': 'MD',
        'zipcode': '20901',
        'description': (
            'Spacious 4-bedroom home in a top-rated school district. '
            'Features a large deck, finished basement, and two-car garage.'
        ),
        'price': 589000,
        'bedrooms': 4,
        'bathrooms': 3.0,
        'garage': 2,
        'sqft': 3100,
        'lot_size': 0.4,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 16, 16, 12),
        'photo_main': 'media/2022/12/04/16/22/home-3.jpg',
        'realtor_name': 'Mark Spencer',
    },
    {
        'title': 'Charming Starter Home',
        'address': '14 Birchwood Ave',
        'city': 'Gaithersburg',
        'state_or_region': 'MD',
        'zipcode': '20877',
        'description': (
            'Perfect starter home with fresh interior paint, updated flooring, '
            'and a private fenced yard. Move-in ready and priced to sell.'
        ),
        'price': 299000,
        'bedrooms': 3,
        'bathrooms': 1.5,
        'garage': 0,
        'sqft': 1400,
        'lot_size': 0.2,
        'is_published': True,
        'listing_date': pendulum.datetime(2022, 4, 16, 16, 14),
        'photo_main': 'media/2022/14/04/16/22/home-5.jpg',
        'realtor_name': 'Alex Rivera',
    },
]


def seed_listings():
    realtor_cache = {r.name: r for r in realtor.objects.all()}
    created = 0
    for data in LISTINGS:
        realtor_name = data['realtor_name']
        realtor_obj = realtor_cache.get(realtor_name)
        if not realtor_obj:
            print(f'  Realtor "{realtor_name}" not found — skipping listing "{data["title"]}"')
            continue

        listing_data = {k: v for k, v in data.items() if k != 'realtor_name'}
        obj, was_created = Listing.objects.get_or_create(
            title=data['title'],
            address=data['address'],
            defaults={**listing_data, 'realtor': realtor_obj},
        )
        if was_created:
            created += 1
            print(f'  Created listing: {obj.title}')
        else:
            print(f'  Skipped (exists): {obj.title}')
    return created

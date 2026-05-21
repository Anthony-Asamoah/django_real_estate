def seed_testimonials():
    from domains.pages.models import Testimonial

    data = [
        {
            'author_name': 'Emmanuel Ofori',
            'author_role': 'Homeowner',
            'body': (
                'They handled everything — from drilling our borehole to completing the '
                'entire building. The team was professional, on time, and the quality '
                'of work exceeded our expectations.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Grace Mensah',
            'author_role': 'Property Developer',
            'body': (
                'I purchased a plot of land through them and they took care of '
                'the construction from foundation to roofing. One team for the whole project — '
                'no headaches dealing with multiple contractors.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Kwame Asante',
            'author_role': 'Business Owner',
            'body': (
                'Our warehouse roof was leaking badly. Their roofing team assessed the '
                'problem the same week and completed repairs ahead of schedule. Highly recommended.'
            ),
            'is_featured': True,
        },
    ]

    created = 0
    for item in data:
        _, was_created = Testimonial.objects.get_or_create(
            author_name=item['author_name'],
            defaults=item,
        )
        if was_created:
            created += 1
            print(f'  Created Testimonial: {item["author_name"]}')
        else:
            print(f'  Skipped (exists): Testimonial — {item["author_name"]}')

    return created

def seed_pages():
    from wagtail.models import Page, Site
    from domains.pages.models import HomePage, AboutPage

    created = 0

    try:
        root_page = Page.objects.get(depth=1)
    except Page.DoesNotExist:
        print('  Root page not found — run migrate first.')
        return 0

    if not HomePage.objects.exists():
        home = HomePage(
            title='Home',
            slug='home',
            body=[
                ('hero', {
                    'heading': 'Property Searching Just Got So Easy',
                    'subtext': (
                        'Lorem ipsum dolor sit, amet consectetur adipisicing elit. '
                        'Recusandae quas, asperiores eveniet vel nostrum magnam '
                        'voluptatum tempore! Consectetur, id commodi!'
                    ),
                }),
                ('services_row', {
                    'heading': 'Services',
                    'services': [
                        {
                            'icon': 'fa-comment',
                            'title': 'Consulting Services',
                            'body': (
                                'Expert consulting for first-time buyers, investors, '
                                'and relocation clients.'
                            ),
                        },
                        {
                            'icon': 'fa-home',
                            'title': 'Property Management',
                            'body': (
                                'Full-service property management: leasing, maintenance, '
                                'and tenant relations.'
                            ),
                        },
                        {
                            'icon': 'fa-suitcase',
                            'title': 'Renting & Selling',
                            'body': (
                                'Competitive market listings with proven negotiation '
                                'strategies to maximise your return.'
                            ),
                        },
                    ],
                }),
            ],
        )
        # Delete Wagtail's default welcome page if it's still the bare Page type
        existing = Page.objects.filter(depth=2).first()
        if existing and type(existing).__name__ == 'Page':
            existing.delete()
            root_page = Page.objects.get(depth=1)  # re-fetch after deletion
        root_page.add_child(instance=home)
        home.save_revision().publish()
        created += 1
        print(f'  Created HomePage: {home.title}')
    else:
        print('  Skipped (exists): HomePage')

    home_page = HomePage.objects.first()

    if not AboutPage.objects.exists():
        about = AboutPage(
            title='About',
            slug='about',
            body=[
                ('rich_text', (
                    '<p>BT Real Estate has been connecting buyers and sellers '
                    'across the DMV area since 2015. Our team of experienced realtors '
                    'specialises in residential, commercial, and luxury properties.</p>'
                    '<p>We pride ourselves on honest guidance, market expertise, '
                    'and personalised service for every client.</p>'
                )),
                ('cta_banner', {
                    'heading': 'We Work For You',
                    'subtext': (
                        'Our agents are available 7 days a week to support your property journey.'
                    ),
                    'button_text': 'View Our Featured Listings',
                    'button_url': '/listings/',
                }),
            ],
        )
        home_page.add_child(instance=about)
        about.save_revision().publish()
        created += 1
        print(f'  Created AboutPage: {about.title}')
    else:
        print('  Skipped (exists): AboutPage')

    # Ensure Site record points to HomePage as root
    if home_page:
        site, site_created = Site.objects.update_or_create(
            pk=1,
            defaults={
                'hostname': 'localhost',
                'port': 8000,
                'site_name': 'BT Real Estate',
                'root_page': home_page,
                'is_default_site': True,
            },
        )
        if site_created:
            print('  Created Site record.')
        else:
            print('  Updated Site record.')

    return created

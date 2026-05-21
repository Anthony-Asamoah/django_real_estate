from pathlib import Path

from django.core.files import File
from wagtail.images.models import Image as WagtailImage

MEDIA_DIR = Path(__file__).parent / 'media'
_image_cache: dict[str, WagtailImage] = {}


def _img(filename: str) -> WagtailImage | None:
    if filename in _image_cache:
        return _image_cache[filename]
    title = filename.rsplit('.', 1)[0].replace('-', ' ').title()
    existing = WagtailImage.objects.filter(title=title).first()
    if existing:
        _image_cache[filename] = existing
        return existing
    path = MEDIA_DIR / filename
    if not path.exists():
        print(f'  Warning: {filename} not found in seeds/media — skipping image')
        return None
    with open(path, 'rb') as f:
        img = WagtailImage(title=title)
        img.file.save(filename, File(f), save=True)
    _image_cache[filename] = img
    return img


def seed_pages():
    from wagtail.models import Page, Site
    from domains.pages.models import (
        HomePage, AboutPage,
        ServicesIndexPage, ServiceDetailPage,
        ProjectsIndexPage, ProjectDetailPage,
        ContactPage, BrandingSettings,
    )

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
            show_featured_projects=True,
            featured_projects_heading='Featured Work',
            body=[
                ('hero_slideshow', {
                    'heading': 'Building Your Vision, From the Ground Up',
                    'subtext': (
                        'Land. Construction. Roofing. Borehole. Property Sales. '
                        'We handle every stage of the build — so you don\'t have to.'
                    ),
                    'slides': [
                        {
                            'image': _img('house-1.jpg'),
                            'caption': 'Quality homes built to last',
                        },
                        {
                            'image': _img('construction.jpg'),
                            'caption': 'Professional construction services',
                        },
                        {
                            'image': _img('building.jpg'),
                            'caption': 'Commercial & residential projects',
                        },
                        {
                            'image': _img('house-2.jpg'),
                            'caption': '',
                        },
                    ],
                    'transition_type': 'fade',
                    'interval': 5000,
                    'animation_speed': 800,
                }),
                ('services_row', {
                    'heading': 'What We Do',
                    'services': [
                        {
                            'icon': 'fa-map',
                            'title': 'Land Acquisition',
                            'body': 'We help you find and secure the right plot of land for your project.',
                        },
                        {
                            'icon': 'fa-hard-hat',
                            'title': 'Construction',
                            'body': 'Full building construction from foundation to finishing, built to last.',
                        },
                        {
                            'icon': 'fa-home',
                            'title': 'Roofing',
                            'body': 'Quality roofing installations and repairs for residential and commercial projects.',
                        },
                    ],
                }),
                ('stats_row', {
                    'heading': '',
                    'stats': [
                        {'value': '150+', 'label': 'Projects Completed', 'icon': 'fa-hard-hat'},
                        {'value': '12', 'label': 'Years of Experience', 'icon': 'fa-calendar'},
                        {'value': '300+', 'label': 'Happy Clients', 'icon': 'fa-smile'},
                        {'value': '5', 'label': 'Core Services', 'icon': 'fa-tools'},
                    ],
                }),
                ('testimonials', {'heading': 'What Our Clients Say'}),
                ('cta_banner', {
                    'heading': 'Ready to Start Your Project?',
                    'subtext': 'Talk to us today — no obligation, just clarity.',
                    'button_text': 'Get in Touch',
                    'button_url': '/contact/',
                }),
            ],
        )
        existing = Page.objects.filter(depth=2).first()
        if existing and type(existing).__name__ == 'Page':
            existing.delete()
            root_page = Page.objects.get(depth=1)
        root_page.add_child(instance=home)
        home.save_revision().publish()
        created += 1
        print(f'  Created HomePage: {home.title}')
    else:
        print('  Skipped (exists): HomePage')

    home_page = HomePage.objects.first()

    # About Page
    _about_body = [
        ('hero_banner', {
            'heading': 'About Us',
            'subtext': 'Building trust, one project at a time.',
        }),
        ('about_intro', {
            'heading': 'We Build More Than Structures',
            'lead': (
                'A full-service building and development company, '
                'delivering from land to completion.'
            ),
            'body': (
                '<p>We are a full-service building and development company serving clients '
                'across the region. From securing land to completing construction, roofing, '
                'and installing boreholes — we manage the entire build lifecycle under one roof.</p>'
                '<p>Our team combines decades of hands-on experience with a commitment to quality, '
                'transparency, and delivering on time. Every project is assigned a dedicated manager '
                'who keeps you informed at every stage.</p>'
            ),
        }),
        ('stats_row', {
            'heading': 'Our Track Record',
            'stats': [
                {'value': '150+', 'label': 'Projects Completed', 'icon': 'fa-hard-hat'},
                {'value': '12', 'label': 'Years of Experience', 'icon': 'fa-calendar'},
                {'value': '300+', 'label': 'Happy Clients', 'icon': 'fa-smile'},
                {'value': '5', 'label': 'Core Services', 'icon': 'fa-tools'},
            ],
        }),
        ('cta_banner', {
            'heading': 'One Team. Every Stage.',
            'subtext': 'We are with you from land to completed property.',
            'button_text': 'See Our Projects',
            'button_url': '/projects/',
        }),
    ]

    if not AboutPage.objects.exists():
        about = AboutPage(title='About', slug='about', body=_about_body)
        home_page.add_child(instance=about)
        about.save_revision().publish()
        created += 1
        print(f'  Created AboutPage: {about.title}')
    else:
        about = AboutPage.objects.first()
        about.body = _about_body
        about.save_revision().publish()
        print('  Updated AboutPage body.')

    # Services Index
    if not ServicesIndexPage.objects.exists():
        services_index = ServicesIndexPage(
            title='Services',
            slug='services',
            body=[
                ('hero_banner', {
                    'heading': 'Our Services',
                    'subtext': 'Everything you need — handled by one trusted team.',
                }),
            ],
        )
        home_page.add_child(instance=services_index)
        services_index.save_revision().publish()
        created += 1
        print(f'  Created ServicesIndexPage: {services_index.title}')

        service_data = [
            {
                'title': 'Land Acquisition & Sales',
                'slug': 'land',
                'hero_heading': 'Land Acquisition & Sales',
                'hero_subtext': 'Find the right plot. We handle valuation, documentation, and transfer.',
                'body_text': (
                    '<p>Whether you are looking to purchase land for personal development or investment, '
                    'we guide you through every step — site visits, valuations, title verification, '
                    'and transfer documentation.</p>'
                    '<p>We also list plots for sale from our portfolio of pre-vetted land across the region.</p>'
                ),
                'steps': [
                    {'step_number': '01', 'title': 'Site Identification',
                     'body': 'We match you with plots that fit your size, location, and budget requirements.'},
                    {'step_number': '02', 'title': 'Due Diligence',
                     'body': 'Full title search, encumbrance checks, and land use verification.'},
                    {'step_number': '03', 'title': 'Valuation & Negotiation',
                     'body': 'Independent valuation and expert negotiation to protect your investment.'},
                    {'step_number': '04', 'title': 'Transfer & Documentation',
                     'body': 'We manage the full legal transfer and land registration process.'},
                ],
            },
            {
                'title': 'Construction',
                'slug': 'construction',
                'hero_heading': 'Construction Services',
                'hero_subtext': 'From foundation to finishing — built right, built to last.',
                'body_text': (
                    '<p>We build residential and commercial structures from the ground up. '
                    'Our construction teams are experienced in all structural types and work '
                    'closely with clients from design through to handover.</p>'
                    '<p>Every project is managed end-to-end with transparent milestones and no hidden costs.</p>'
                ),
                'steps': [
                    {'step_number': '01', 'title': 'Design & Planning',
                     'body': 'We work with your architect or connect you with ours to finalise plans and permits.'},
                    {'step_number': '02', 'title': 'Foundation & Structure',
                     'body': 'Solid foundations using certified materials and experienced structural teams.'},
                    {'step_number': '03', 'title': 'Build & Finishing',
                     'body': 'Full construction including masonry, plastering, tiling, and all interior finishes.'},
                    {'step_number': '04', 'title': 'Handover',
                     'body': 'Final inspection, snag resolution, and formal handover with full documentation.'},
                ],
            },
            {
                'title': 'Roofing',
                'slug': 'roofing',
                'hero_heading': 'Roofing Services',
                'hero_subtext': 'New installations, re-roofing, and repairs — done right the first time.',
                'body_text': (
                    '<p>We supply and install a full range of roofing systems for both new builds and '
                    'existing structures. Whether you need a complete new roof, a partial replacement, '
                    'or urgent leak repairs, our roofing team responds quickly with lasting solutions.</p>'
                ),
                'steps': [
                    {'step_number': '01', 'title': 'Assessment',
                     'body': 'Thorough roof inspection to identify damage, structural issues, or design requirements.'},
                    {'step_number': '02', 'title': 'Material Selection',
                     'body': 'We recommend the right roofing system for your structure, climate, and budget.'},
                    {'step_number': '03', 'title': 'Installation',
                     'body': 'Professional installation by certified roofers with full site safety measures.'},
                    {'step_number': '04', 'title': 'Warranty & Maintenance',
                     'body': 'All installations come with a workmanship warranty and optional maintenance plans.'},
                ],
            },
            {
                'title': 'Borehole Drilling',
                'slug': 'borehole',
                'hero_heading': 'Borehole Drilling',
                'hero_subtext': 'Reliable water supply for homes, farms, and commercial sites.',
                'body_text': (
                    '<p>We provide professional borehole drilling and installation services for '
                    'residential, agricultural, and commercial clients. Our hydrogeological surveys '
                    'ensure we drill in the right location every time, minimising dry holes and cost overruns.</p>'
                ),
                'steps': [
                    {'step_number': '01', 'title': 'Hydrogeological Survey',
                     'body': 'Site survey to identify the best drilling location and estimate expected yield.'},
                    {'step_number': '02', 'title': 'Drilling',
                     'body': 'Precision drilling using modern equipment to reach the water table safely.'},
                    {'step_number': '03', 'title': 'Casing & Development',
                     'body': 'Borehole cased, developed, and tested for sustainable yield and water quality.'},
                    {'step_number': '04', 'title': 'Pump Installation',
                     'body': 'Submersible pump fitted and connected to your storage or distribution system.'},
                ],
            },
            {
                'title': 'Property Sales',
                'slug': 'property-sales',
                'hero_heading': 'Property Sales',
                'hero_subtext': 'Buy a completed home — no construction stress, just move in.',
                'body_text': (
                    '<p>We sell completed properties built to our quality standards. '
                    'Each property has been through our full construction process and is '
                    'ready for immediate occupation. Browse our current listings for available homes.</p>'
                ),
                'steps': [
                    {'step_number': '01', 'title': 'Browse Listings',
                     'body': 'View our portfolio of completed properties available for sale.'},
                    {'step_number': '02', 'title': 'Site Visit',
                     'body': 'Schedule a viewing — our team will walk you through every detail.'},
                    {'step_number': '03', 'title': 'Offer & Agreement',
                     'body': 'We handle the sale agreement, valuation, and legal documentation.'},
                    {'step_number': '04', 'title': 'Keys in Hand',
                     'body': 'Smooth transfer of ownership — you move in, we follow up.'},
                ],
            },
        ]

        for svc in service_data:
            page = ServiceDetailPage(
                title=svc['title'],
                slug=svc['slug'],
                body=[
                    ('hero_banner', {
                        'heading': svc['hero_heading'],
                        'subtext': svc['hero_subtext'],
                    }),
                    ('rich_text', svc['body_text']),
                    ('process_steps', {
                        'heading': 'How It Works',
                        'steps': svc['steps'],
                    }),
                    ('cta_banner', {
                        'heading': 'Ready to Get Started?',
                        'subtext': 'Contact us for a free consultation.',
                        'button_text': 'Contact Us',
                        'button_url': '/contact/',
                    }),
                ],
            )
            services_index.add_child(instance=page)
            page.save_revision().publish()
            created += 1
            print(f'  Created ServiceDetailPage: {page.title}')
    else:
        print('  Skipped (exists): ServicesIndexPage')

    # Projects Index
    if not ProjectsIndexPage.objects.exists():
        projects_index = ProjectsIndexPage(
            title='Projects',
            slug='projects',
            body=[
                ('hero_banner', {
                    'heading': 'Our Projects',
                    'subtext': 'A selection of work we are proud of.',
                }),
                ('cta_banner', {
                    'heading': 'Have a Project in Mind?',
                    'subtext': 'We would love to hear about it.',
                    'button_text': 'Contact Us',
                    'button_url': '/contact/',
                }),
            ],
        )
        home_page.add_child(instance=projects_index)
        projects_index.save_revision().publish()
        created += 1
        print(f'  Created ProjectsIndexPage: {projects_index.title}')

        # Sample project stubs (no images — editors will fill in)
        sample_projects = [
            {
                'title': '4-Bedroom Residential Build — Kumasi',
                'slug': 'residential-build-kumasi',
                'location': 'Kumasi, Ashanti Region',
                'service_slug': 'construction',
                'hero_subtext': 'Full construction from foundation to finishing, delivered on time.',
                'body_text': (
                    '<p>A complete four-bedroom residential build delivered over eight months. '
                    'We handled full construction from foundation to finishing, including plumbing, '
                    'electrical, and interior fit-out.</p>'
                ),
            },
            {
                'title': 'Commercial Roofing Replacement — Accra',
                'slug': 'commercial-roofing-accra',
                'location': 'Accra, Greater Accra',
                'service_slug': 'roofing',
                'hero_subtext': 'Full roof replacement for a commercial warehouse in Greater Accra.',
                'body_text': (
                    '<p>Full roof replacement for a commercial warehouse. The project involved '
                    'removing the existing deteriorated roofing, structural repairs to the trusses, '
                    'and installation of long-span aluminium roofing sheets.</p>'
                ),
            },
            {
                'title': 'Borehole Installation — Farm Estate, Brong-Ahafo',
                'slug': 'borehole-brong-ahafo',
                'location': 'Brong-Ahafo Region',
                'service_slug': 'borehole',
                'hero_subtext': 'Site survey, drilling, and pump installation for a large agricultural estate.',
                'body_text': (
                    '<p>Site survey, 80-metre borehole drilling, casing, development, and submersible '
                    'pump installation for a large agricultural estate. The borehole now supplies '
                    'irrigation and domestic water to the property.</p>'
                ),
            },
        ]

        construction_page = ServiceDetailPage.objects.filter(slug='construction').first()
        roofing_page = ServiceDetailPage.objects.filter(slug='roofing').first()
        borehole_page = ServiceDetailPage.objects.filter(slug='borehole').first()
        service_map = {
            'construction': construction_page,
            'roofing': roofing_page,
            'borehole': borehole_page,
        }

        for proj in sample_projects:
            project_page = ProjectDetailPage(
                title=proj['title'],
                slug=proj['slug'],
                location=proj['location'],
                service=service_map.get(proj['service_slug']),
                body=[
                    ('hero_banner', {
                        'heading': proj['title'],
                        'subtext': proj['hero_subtext'],
                    }),
                    ('rich_text', proj['body_text']),
                ],
            )
            projects_index.add_child(instance=project_page)
            project_page.save_revision().publish()
            created += 1
            print(f'  Created ProjectDetailPage: {project_page.title}')
    else:
        print('  Skipped (exists): ProjectsIndexPage')

    # Contact Page
    if not ContactPage.objects.exists():
        contact = ContactPage(
            title='Contact',
            slug='contact',
            body=[
                ('hero_banner', {
                    'heading': 'Contact Us',
                    'subtext': 'We are ready to help — reach out today.',
                }),
            ],
        )
        home_page.add_child(instance=contact)
        contact.save_revision().publish()
        created += 1
        print(f'  Created ContactPage: {contact.title}')
    else:
        print('  Skipped (exists): ContactPage')

    # Ensure Site record points to HomePage
    if home_page:
        site, site_created = Site.objects.update_or_create(
            pk=1,
            defaults={
                'hostname': 'localhost',
                'port': 8000,
                'site_name': 'Real Estate',
                'root_page': home_page,
                'is_default_site': True,
            },
        )
        if site_created:
            print('  Created Site record.')
        else:
            print('  Updated Site record.')

    # BrandingSettings — tied to the default site (BaseSiteSetting)
    default_site = Site.objects.filter(is_default_site=True).first()
    if default_site:
        branding, _ = BrandingSettings.objects.get_or_create(site=default_site)
        branding.site_name = 'Numira Real Estate'
        branding.phone = '0247737950'
        branding.email = 'sumailainusah5@gmail.com'
        branding.instagram_url = 'https://www.instagram.com/numiralreal/'
        branding.tiktok_url = 'https://www.tiktok.com/@numiral.real.estat'
        branding.save()
        print('  Updated BrandingSettings.')

    return created

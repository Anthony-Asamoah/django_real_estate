from pathlib import Path

import pendulum
from django.core.files import File
from wagtail.images.models import Image as WagtailImage

from domains.employees.models import Employee
from domains.projects.models import (
    STATUS_AVAILABLE,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_SOLD,
    Project,
)

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
        print(f'  Warning: {filename} not found in seeds/media — skipping photo')
        return None
    with open(path, 'rb') as f:
        img = WagtailImage(title=title)
        img.file.save(filename, File(f), save=True)
    _image_cache[filename] = img
    return img


PROJECTS = [
    # ── LAND ACQUISITION & SALES ────────────────────────────────────────────
    {
        'title': 'Serviced Plot — Tamale Road',
        'address': 'Plot 22A, Tamale Road Corridor',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Quarter-acre serviced plot along the busy Tamale–Bolgatanga highway corridor. '
            'Water, electricity, and paved road access all in place. Title deed available.'
        ),
        'price': 95000,
        'land_area_sqft': 10890,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2022, 9, 18),
        'photo_main': 'land-site-1.webp',
        'photo_1': 'land-site-2.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'land',
    },
    {
        'title': 'Serviced Plots — Zuarungu Extension',
        'address': 'Zuarungu Extension, Phase 2',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            '6 individually titled serviced plots ranging from 0.2 to 0.3 acres. '
            'Water and electricity at the boundary, internal access road complete. '
            'Indenture and site plan provided on purchase.'
        ),
        'price': 88000,
        'land_area_sqft': 12000,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 12, 1),
        'photo_main': 'land-site-2.jpg',
        'photo_1': 'land-site-1.webp',
        'employee_name': 'Ama Boateng',
        'service_slug': 'land',
    },
    {
        'title': 'Corner Plot — Bolgatanga Ring Road',
        'address': 'Plot 4, Ring Road Extension',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Prime corner plot on the Ring Road extension, ideal for commercial or residential development. '
            'Elevated location with good drainage. Registered title deed and survey plan included.'
        ),
        'price': 115000,
        'land_area_sqft': 13200,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 1, 20),
        'photo_main': 'land-site-1.webp',
        'employee_name': 'Ama Boateng',
        'service_slug': 'land',
    },
    {
        'title': 'Commercial Plot — Zuarungu Main Road',
        'address': 'Zuarungu Main Road, Near Market Junction',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Half-acre commercial plot fronting Zuarungu Main Road, sold to a retail developer. '
            'High-traffic location with existing utility connections. Title transfer completed.'
        ),
        'price': 210000,
        'land_area_sqft': 21780,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 6, 14),
        'photo_main': 'land-site-2.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'land',
    },

    # ── PROPERTY SALES ──────────────────────────────────────────────────────
    {
        'title': '3-Bedroom House — Zuarungu',
        'address': 'Plot 14, Zuarungu Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'A beautifully finished 3-bedroom detached house in the quiet Zuarungu suburb. '
            'Features tiled floors, fitted kitchen, screened windows, and a large compound. '
            'Situated 5 minutes from Bolgatanga Central.'
        ),
        'price': 280000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'garage': 1,
        'sqft': 1800,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2022, 3, 10),
        'photo_main': 'completed-house-white-with-porch.jpg',
        'photo_1': 'completed-interior-white-living-space.jpg',
        'photo_2': 'completed-interior-white-bedroom.jpg',
        'photo_3': 'completed-interior-white-bathroom.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '2-Bedroom Bungalow — Sumbrungu',
        'address': 'Plot 7, Sumbrungu Extension',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Compact and comfortable 2-bedroom bungalow ideal for a small family. '
            'Located in the growing Sumbrungu residential area with easy access to the main road.'
        ),
        'price': 165000,
        'bedrooms': 2,
        'bathrooms': 1.0,
        'sqft': 1100,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2022, 6, 5),
        'photo_main': 'completed-house-with-hedge.webp',
        'photo_1': 'completed-interior-white-bedroom.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'property-sales',
    },
    {
        'title': '4-Bedroom House — Tanga Junction',
        'address': 'Plot 3, Tanga Junction Area',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Spacious 4-bedroom detached home at the Tanga Junction area. '
            'Features en-suite master bedroom, tiled throughout, security fence, and borehole. '
            'Sold off-plan and completed to the client\'s specifications.'
        ),
        'price': 390000,
        'bedrooms': 4,
        'bathrooms': 3.0,
        'garage': 2,
        'sqft': 2600,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2023, 10, 5),
        'photo_main': 'completed-house-2-story-deluxe.jpg',
        'photo_1': 'completed-interior-white-bathroom.jpg',
        'photo_2': 'completed-interior-white-bedroom.jpg',
        'photo_3': 'completed-interior-bedroom-closet-1.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '4-Bedroom Executive Home — Tamale Road',
        'address': 'Plot 1, Tamale Road Executive Estate',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Brand-new 4-bedroom executive home on the prestigious Tamale Road corridor. '
            'En-suite master, open-plan living, Italian tiles, fitted wardrobes, '
            'fully fenced compound with electric gate, and a private borehole. '
            'Ready for immediate occupancy.'
        ),
        'price': 480000,
        'bedrooms': 4,
        'bathrooms': 3.0,
        'garage': 2,
        'sqft': 3000,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 8, 20),
        'photo_main': 'completed-house-deluxe.jpg',
        'photo_1': 'compeleted-interior-white-kitchen.jpg',
        'photo_2': 'completed-interior-white-living-space.jpg',
        'photo_3': 'completed-interior-white-bathroom.jpg',
        'photo_4': 'completed-interior-bedroom-closet-1.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '3-Bedroom Townhouse — Bolgatanga Central',
        'address': 'Plot 5, Hospital Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Modern 3-bedroom townhouse walking distance from Bolgatanga Central Market. '
            'Tiled floors, security bars, large rooftop terrace, and single lock-up garage. '
            'Suitable for residential or professional use.'
        ),
        'price': 340000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'garage': 1,
        'sqft': 2100,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 10, 10),
        'photo_main': 'completed-house-white-2-story.jpg',
        'photo_1': 'completed-interior-white-bedroom.jpg',
        'photo_2': 'completed-interior-white-bathroom.jpg',
        'photo_3': 'completed-interior-white-living-space.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '2-Bedroom Starter Home — Gambibgo',
        'address': 'Plot 18, Gambibgo Residential Area',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Affordable 2-bedroom home in the up-and-coming Gambibgo neighbourhood. '
            'Quality block construction, plastered and painted, with concrete verandah. '
            'Perfect first home or buy-to-let investment.'
        ),
        'price': 195000,
        'bedrooms': 2,
        'bathrooms': 1.0,
        'sqft': 1200,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 1, 15),
        'photo_main': 'completed-estate-white.jpg',
        'photo_1': 'completed-interior-white-bathroom.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'property-sales',
    },
    {
        'title': '5-Bedroom Mansion — Navrongo Road',
        'address': 'Plot 2, Navrongo Road Executive Area',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Luxury 5-bedroom detached mansion with double living areas, en-suite bathrooms '
            'to all rooms, imported tiles, and a spacious walled compound. '
            'Solar backup, borehole, and 3-car garage included. Ready for viewing.'
        ),
        'price': 750000,
        'bedrooms': 5,
        'bathrooms': 4.0,
        'garage': 3,
        'sqft': 4200,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 4, 1),
        'photo_main': 'completed-house-tall-with-lawn.jpg',
        'photo_1': 'completed-interior-bedroom-closet-1.jpg',
        'photo_2': 'completed-interior-white-living-space.jpg',
        'photo_3': 'completed-interior-white-bathroom.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '3-Bedroom Duplex — Bolgatanga New Town',
        'address': 'Plot 6, New Town Extension',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'A stylish 3-bedroom duplex with open-plan ground floor, 2 upstairs en-suites, '
            'and a rooftop terrace. Originally built for an overseas client and recently released for sale.'
        ),
        'price': 420000,
        'bedrooms': 3,
        'bathrooms': 3.0,
        'garage': 1,
        'sqft': 2800,
        'status': STATUS_SOLD,
        'is_published': True,
        'project_date': pendulum.datetime(2024, 5, 22),
        'photo_main': 'completed-white-and-brown-2-story.jpg',
        'photo_1': 'completed-interior-white-living-space.jpg',
        'photo_2': 'completed-interior-white-bedroom.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },
    {
        'title': '2-Story Family Home — Bolgatanga East',
        'address': 'Plot 9, Bolgatanga East New Estate',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Newly completed 3-bedroom 2-storey family home with generous living spaces, '
            'modern kitchen, and a fully tiled master en-suite. '
            'Secure compound with car parking. Available for immediate purchase.'
        ),
        'price': 370000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'garage': 1,
        'sqft': 2300,
        'status': STATUS_AVAILABLE,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 3, 10),
        'photo_main': 'completed-estate-2-stories.webp',
        'photo_1': 'compeleted-interior-white-kitchen.jpg',
        'photo_2': 'completed-interior-white-bedroom.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'property-sales',
    },

    # ── CONSTRUCTION ────────────────────────────────────────────────────────
    {
        'title': 'Semi-Detached Duplex (2 Units) — Bongo Road',
        'address': 'Plot 9, Bongo Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Two mirror-image 3-bedroom semi-detached units currently at lintel level. '
            'Each unit has a private compound, 2 bathrooms, and covered car park. '
            'Expected handover in Q3 2026.'
        ),
        'price': 520000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'sqft': 2200,
        'status': STATUS_IN_PROGRESS,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 11, 1),
        'photo_main': 'construction-building-no-roof.jpg',
        'photo_1': 'construction-estate-foundations.jpg',
        'employee_name': 'Abena Mensah',
        'service_slug': 'construction',
    },
    {
        'title': 'Internal Road Network — Gambibgo New Estate',
        'address': 'Gambibgo Estate, Off Bongo Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            '1.8 km of engineered internal roads with concrete kerbing, drainage channels, '
            'and street lighting for a 42-plot residential estate. '
            'Project delivered 3 weeks ahead of schedule.'
        ),
        'price': 385000,
        'land_area_sqft': 210000,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2023, 4, 14),
        'photo_main': 'construction.jpg',
        'photo_1': 'building.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },
    {
        'title': 'Drainage System — SSNIT Residential Zone',
        'address': 'SSNIT Flats, Hospital Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Design and construction of a storm-water drainage system covering 320 metres '
            'to eliminate annual flooding in the SSNIT residential zone. '
            'Includes concrete channels, culverts, and catchment pits.'
        ),
        'price': 210000,
        'land_area_sqft': 85000,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2023, 7, 30),
        'photo_main': 'construction-estate-foundations.jpg',
        'photo_1': 'construction.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },
    {
        'title': 'Road & Kerbing — Frafra Estate, Nangodi Road',
        'address': 'Frafra Estate, Nangodi Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Earthworks, grading, gravel surfacing, and concrete kerbing for a new 28-plot estate. '
            '60% complete. Full project includes drainage and signage.'
        ),
        'price': 295000,
        'land_area_sqft': 145000,
        'status': STATUS_IN_PROGRESS,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 2, 14),
        'photo_main': 'construction.jpg',
        'photo_1': 'construction-building-no-roof.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },
    {
        'title': 'Perimeter Wall & Gate — Kalbeo Residential Plot',
        'address': 'Plot 11, Kalbeo Junction',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Full perimeter blockwall, 4-metre sliding steel gate, and security lighting '
            'for a corner residential plot. Project includes concrete coping and plastered finish. '
            'Completed in 6 weeks.'
        ),
        'price': 38000,
        'land_area_sqft': 8700,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2024, 2, 12),
        'photo_main': 'building.jpg',
        'photo_1': 'construction-estate-foundations.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },
    {
        'title': 'Solar Street Lighting — Zebilla Township',
        'address': 'Zebilla Main Road & Junctions',
        'city': 'Zebilla',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Design and installation of 35 solar-powered street lights across 4 key junctions '
            'in Zebilla Township. Work is 40% complete — pole erection done, wiring in progress. '
            'Commissioned by the district assembly.'
        ),
        'price': 180000,
        'status': STATUS_IN_PROGRESS,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 4, 10),
        'photo_main': 'construction.jpg',
        'photo_1': 'building.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },
    {
        'title': 'Foundation & Shell — Soe Estate, Bolgatanga',
        'address': 'Plot 3, Soe Estate Extension',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Foundation, blockwork, and shell construction for a 4-bedroom family home. '
            'Currently at roof level — roofing and finishing works to follow. '
            'Client-supervised project with full milestone reporting.'
        ),
        'price': 230000,
        'bedrooms': 4,
        'bathrooms': 2.0,
        'sqft': 2400,
        'status': STATUS_IN_PROGRESS,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 5, 1),
        'photo_main': 'construction-estate-foundations.jpg',
        'photo_1': 'construction-building-no-roof.jpg',
        'employee_name': 'Kofi Asante',
        'service_slug': 'construction',
    },

    # ── ROOFING ─────────────────────────────────────────────────────────────
    {
        'title': 'Roof Replacement — Bolga Central Secondary School',
        'address': 'Bolgatanga Central Secondary School',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Full aluminium roof replacement across 6 classroom blocks and the administration wing. '
            'Completed during school vacation to avoid disruption. '
            'Comes with a 15-year workmanship warranty.'
        ),
        'price': 72000,
        'sqft': 9500,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2023, 1, 20),
        'photo_main': 'completed-roofing-on--unpainted-house.jpg',
        'photo_1': 'roofing-almost-completed.avif',
        'employee_name': 'Kofi Asante',
        'service_slug': 'roofing',
    },
    {
        'title': 'Roofing — 6-Unit Apartment Block, Bolgatanga',
        'address': 'Block C, Zuarungu Road Apartments',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'Complete roofing works for a newly completed 6-unit apartment block. '
            'Long-span aluminium sheets, ridge capping, guttering, and downpipes installed. '
            'Delivered within the 3-week schedule agreed with the main contractor.'
        ),
        'price': 55000,
        'sqft': 6800,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2024, 9, 5),
        'photo_main': 'roofing-1.webp',
        'photo_1': 'completed-roofing-on--unpainted-house.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'roofing',
    },
    {
        'title': 'Roof Installation — Nangodi Road Residence',
        'address': 'Plot 17, Nangodi Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            'New aluminium sheet roof installation on a 3-bedroom residential property. '
            'Includes full timber frame, ridge capping, guttering, and ceiling board. '
            'Project completed on time with no disruption to the ongoing interior works.'
        ),
        'price': 28000,
        'sqft': 2200,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2024, 11, 18),
        'photo_main': 'roofing-almost-completed.avif',
        'photo_1': 'completed-roofing-on--unpainted-house.jpg',
        'employee_name': 'Ama Boateng',
        'service_slug': 'roofing',
    },

    # ── BOREHOLE DRILLING ───────────────────────────────────────────────────
    {
        'title': 'Borehole Installation — Nangodi Road Clinic',
        'address': 'Nangodi Road, near Health Centre',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            '120-metre mechanised borehole installed for the Nangodi Road community health clinic. '
            'Includes solar-powered pump, overhead tank, and reticulation to all water points. '
            'Now serving over 800 patients and staff monthly.'
        ),
        'price': 48000,
        'land_area_sqft': 500,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2022, 11, 3),
        'photo_main': 'borehole-site-1.webp',
        'photo_1': 'borehole-2.webp',
        'employee_name': 'Kofi Asante',
        'service_slug': 'borehole',
    },
    {
        'title': 'Borehole Drilling — Sumbrungu Community School',
        'address': 'Sumbrungu, Off Bolgatanga–Navrongo Road',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            '150-metre deep mechanised borehole for a community primary school. '
            'Work ongoing — casing, pump installation, and solar system to follow. '
            'Target completion: May 2026.'
        ),
        'price': 52000,
        'status': STATUS_IN_PROGRESS,
        'is_published': True,
        'project_date': pendulum.datetime(2026, 3, 1),
        'photo_main': 'borehole-2.webp',
        'photo_1': 'borehole-site-1.webp',
        'employee_name': 'Kofi Asante',
        'service_slug': 'borehole',
    },
    {
        'title': 'Borehole — Kalbeo Community Centre',
        'address': 'Kalbeo Junction Community Centre',
        'city': 'Bolgatanga',
        'state_or_region': 'Upper East Region',
        'zipcode': '',
        'description': (
            '100-metre borehole drilled and equipped for the Kalbeo Community Centre. '
            'Submersible pump connected to a 5,000-litre overhead tank serving the centre '
            'and surrounding households. Hydro-survey completed before drilling.'
        ),
        'price': 42000,
        'status': STATUS_COMPLETED,
        'is_published': True,
        'project_date': pendulum.datetime(2025, 4, 22),
        'photo_main': 'borehole-site-1.webp',
        'photo_1': 'borehole-2.webp',
        'employee_name': 'Kofi Asante',
        'service_slug': 'borehole',
    },
]

_PHOTO_FIELDS = ['photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6']


def seed_projects():
    from domains.pages.models import ServiceDetailPage

    employee_cache = {e.name: e for e in Employee.objects.all()}
    service_cache = {s.slug: s for s in ServiceDetailPage.objects.live()}
    created = 0

    for data in PROJECTS:
        employee_name = data.pop('employee_name')
        service_slug = data.pop('service_slug', None)
        employee_obj = employee_cache.get(employee_name)
        if not employee_obj:
            print(f'  Employee "{employee_name}" not found — skipping "{data["title"]}"')
            continue

        # Pull photo filenames out before get_or_create
        photo_files = {field: data.pop(field, None) for field in _PHOTO_FIELDS}

        obj, was_created = Project.objects.get_or_create(
            title=data['title'],
            address=data['address'],
            defaults={**data, 'employee': employee_obj},
        )

        # Assign photos and service on create; update service on existing records
        dirty = False
        if was_created:
            for field, filename in photo_files.items():
                if filename:
                    img = _img(filename)
                    if img:
                        setattr(obj, field, img)
                        dirty = True
            created += 1
            print(f'  Created project: {obj.title}')
        else:
            print(f'  Skipped (exists): {obj.title}')

        if service_slug:
            service_obj = service_cache.get(service_slug)
            if service_obj:
                if obj.service_id != service_obj.pk:
                    obj.service = service_obj
                    dirty = True
            else:
                print(f'  Warning: ServiceDetailPage slug="{service_slug}" not found — service not assigned')

        if dirty:
            obj.save()

    return created

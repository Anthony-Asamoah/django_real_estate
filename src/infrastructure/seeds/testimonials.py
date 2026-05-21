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
        {
            'author_name': 'Abuuri Yirijor',
            'author_role': 'Landowner',
            'body': (
                'I am very satisfied with the professionalism and efficiency of the company during my recent '
                'land acquisition. The entire process was transparent, and all documentation was clearly '
                'explained and handled without delay. I would confidently recommend them to anyone looking '
                'for genuine and secure land services.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Amina Tengaana',
            'author_role': 'Property Owner',
            'body': (
                'The construction work carried out on my property was excellent from start to finish. '
                'The team demonstrated strong attention to detail, maintained good communication, and '
                'delivered within the agreed timeline. The final structure exceeded my expectations in '
                'both quality and finish.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Ziblim Naaba',
            'author_role': 'Homeowner',
            'body': (
                'I engaged them for roofing services, and the result was outstanding. The materials used '
                'were durable and of high quality, and the workmanship was precise. Even after completion, '
                'the roof has held up perfectly against heavy rains.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Saalim Kpieta',
            'author_role': 'Homeowner',
            'body': (
                'I appreciate the borehole drilling service they provided for my home. The water yield is '
                'strong and consistent, and the installation process was smooth and well managed. Their '
                'technical expertise in water solutions is impressive.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Awaaba Jirapa',
            'author_role': 'Landowner',
            'body': (
                'Buying land through this company was a stress-free experience. They provided all necessary '
                'verification documents and ensured I was fully informed before making any commitment. '
                'Their honesty and clarity gave me great confidence.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Issaka Gbeogo',
            'author_role': 'Property Developer',
            'body': (
                'The building project they handled for me was executed with high standards. From foundation '
                'to finishing, every stage was carefully supervised. I am very pleased with the durability '
                'and modern design of the structure.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Mariam Balure',
            'author_role': 'Homeowner',
            'body': (
                'Their roofing team did a fantastic job replacing my old roof. They worked quickly but '
                'without compromising quality. The site was also kept clean throughout the project, '
                'which I truly appreciated.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Haruna Kando',
            'author_role': 'Landowner',
            'body': (
                'I purchased land through them and was impressed by their professionalism and integrity. '
                'All legal checks were handled properly, and I received full support even after the '
                'purchase was completed.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Fatima Yempini',
            'author_role': 'Homeowner',
            'body': (
                'The borehole installation service was excellent. They assessed the best location, carried '
                'out the drilling efficiently, and ensured everything was functioning properly before '
                'leaving. The water supply has been reliable ever since.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Alhassan Tia',
            'author_role': 'Property Developer',
            'body': (
                'I contracted them for a full construction project, and the outcome was excellent. Their '
                'coordination, skilled labor, and commitment to quality made the entire process smooth. '
                'I would gladly work with them again in the future.'
            ),
            'is_featured': True,
        },

        # Long-form testimonials (3 paragraphs each)
        {
            'author_name': 'Abukari Tampuri',
            'author_role': 'Homeowner',
            'body': (
                'I first heard about this company through a neighbour who had used them for borehole drilling, '
                'and after seeing the quality of their work firsthand, I decided to engage them for a full '
                'three-bedroom house construction on my plot in Bolgatanga. From the very first meeting, their '
                'team was thorough in understanding exactly what I needed and realistic about timelines and costs. '
                'There were no hidden charges and no surprises — everything was laid out clearly before work began.\n\n'
                'Throughout the construction process, I was kept informed at every stage. The site supervisor '
                'called me regularly with updates, and I was invited to inspect the work at key milestones — '
                'foundation, lintel level, and roofing. Any concerns I raised were addressed promptly and '
                'without argument. The workers were disciplined, the site was well managed, and the materials '
                'delivered matched exactly what was specified in the agreement.\n\n'
                'When the project was finally completed, I was genuinely moved by the quality of what had been '
                'built. The finishing — tiling, plastering, painting, and electrical work — was done to a very '
                'high standard. I have since recommended this company to three of my relatives, all of whom '
                'have had equally positive experiences. I have no hesitation in saying they are the best '
                'building company I have worked with in this region.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Zenabou Asigri',
            'author_role': 'Property Developer',
            'body': (
                'As someone who has been involved in property development for over a decade, I have worked '
                'with many contractors across the Upper East Region. What sets this company apart is not just '
                'the technical skill of their workers, but the organisation and professionalism of their entire '
                'operation. When I engaged them to construct two semi-detached units on my land near Navrongo '
                'Road, I came in with high expectations — and they were met at every turn.\n\n'
                'The project management was exceptional. A clear schedule was drawn up before groundbreaking, '
                'and it was followed closely throughout. When we encountered a delay due to a materials '
                'shortage mid-project, they communicated the issue immediately, proposed a solution, and '
                'adjusted the schedule accordingly without pushing the final deadline. That level of '
                'transparency is rare and deeply appreciated in this industry.\n\n'
                'The finished units have attracted significant interest from prospective tenants, and several '
                'people have commented specifically on the quality of the construction and design. I am already '
                'in discussions with the company about a third project — a larger residential development. '
                'For any serious property developer in northern Ghana, I would say this is the team to work '
                'with without reservation.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Mahama Sugri',
            'author_role': 'Landowner',
            'body': (
                'I had been trying to secure a plot of land near the Tamale Road corridor for almost two years '
                'before I was introduced to this company. Previous attempts had involved unreliable agents, '
                'unclear documentation, and at least one near-fraudulent transaction that I narrowly avoided. '
                'When I approached this company, the difference was immediately apparent. They were upfront '
                'about what land was available, provided site plans and documentation from the outset, and '
                'gave me time to carry out my own due diligence before committing.\n\n'
                'The transaction itself was handled with complete professionalism. All paperwork was prepared '
                'accurately, witnessed appropriately, and handed to me in full — including a site plan, '
                'indenture, and receipt. I was also guided through the process of registering the land at the '
                'Lands Commission, which I had not done before. Their staff were patient and knowledgeable, '
                'and I never felt rushed or pressured at any point.\n\n'
                'Having secured the land, I then contracted the same company to begin construction of a '
                'two-bedroom structure. The continuity of working with one trusted team for both the land '
                'purchase and the build made the entire process far smoother than I had anticipated. I now '
                'have a completed property and peace of mind that everything was done properly and legally. '
                'I am deeply grateful for the service I received.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Ayishatu Boafo',
            'author_role': 'Community Representative',
            'body': (
                'Our community had struggled for years with access to clean water. The only borehole in the '
                'area had broken down, and attempts to repair it through other contractors had failed twice. '
                'When we approached this company, they conducted a proper site assessment before making any '
                'promises, which gave us confidence that they understood the technical challenges involved. '
                'They were honest about the depth likely needed and the expected yield, and they advised us '
                'on the most suitable pump system for our community size.\n\n'
                'The drilling was completed within the projected timeframe and at the agreed cost. The crew '
                'was respectful of the community, worked efficiently, and took care to minimise disruption '
                'to the area around the drilling site. The company also arranged for a brief training session '
                'with community members on basic maintenance of the pump system, which showed that their '
                'interest went beyond just completing the job and collecting payment.\n\n'
                'The borehole has now been in operation for several months and has transformed daily life '
                'for over three hundred households. Women and children no longer have to walk long distances '
                'to fetch water, and waterborne illness in the community has noticeably reduced. On behalf '
                'of our community, I want to express our deep gratitude and wholehearted recommendation of '
                'this company to any organisation or individual in need of reliable water solutions.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Seidu Danaa',
            'author_role': 'Business Owner',
            'body': (
                'I contracted this company to construct a commercial storage facility on my land outside '
                'Bolgatanga town, and I can say with full confidence that the experience exceeded everything '
                'I had hoped for. Before engaging them, I had received quotes from several other builders, '
                'and while their price was not the lowest, the detail and clarity of their proposal stood '
                'out immediately. They itemised everything — materials, labour, equipment, timeline — and '
                'were willing to explain any line item I queried. That transparency convinced me to proceed '
                'with them.\n\n'
                'During construction, the professionalism of the on-site team was consistent throughout. '
                'The supervisor visited the site daily, the workers maintained discipline, and the quality '
                'of materials used matched exactly what had been specified. When I visited unannounced on '
                'several occasions, I always found the work progressing as expected and the site in good '
                'order. One minor structural adjustment was required midway through, and it was handled '
                'swiftly and at no additional cost, which I considered a mark of genuine integrity.\n\n'
                'The facility was completed on time and has been in full commercial use ever since. The '
                'structure is solid, the roofing has proven watertight through two rainy seasons, and '
                'the internal layout works exactly as I planned. I have already referred two business '
                'associates to this company, and both have since reported very positive outcomes. '
                'They are, without question, the most reliable building company I have encountered '
                'in this part of the country.'
            ),
            'is_featured': True,
        },

        # Short testimonials (two lines each)
        {
            'author_name': 'Fati Achana',
            'author_role': 'Homeowner',
            'body': (
                'The team was efficient, respectful, and the work was done exactly as agreed. '
                'I would not hesitate to use them again for any future project.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Yakubu Nabilgu',
            'author_role': 'Landowner',
            'body': (
                'Buying land through them was smooth and completely stress-free from start to finish. '
                'All documents were in order and delivered promptly — highly recommended.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Ramatu Dery',
            'author_role': 'Property Owner',
            'body': (
                'Excellent roofing work completed ahead of schedule and within budget. '
                'The quality of materials and craftsmanship was clearly of the highest standard.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Bawa Sissala',
            'author_role': 'Homeowner',
            'body': (
                'Our borehole was drilled and installed without any issues — clean water on the first day. '
                'The crew were professional and left the site tidy when they were done.'
            ),
            'is_featured': True,
        },
        {
            'author_name': 'Naomi Atule',
            'author_role': 'Property Developer',
            'body': (
                'Fast, reliable, and honest — three words that perfectly describe this company. '
                'The construction project was delivered on time and the finish was impeccable.'
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

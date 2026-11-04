from django.db import migrations


def enable_for_land(apps, schema_editor):
    """Pilot default: turn land plan annotations on for the seeded 'land' service (admins can change it in settings)."""
    ServiceDetailPage = apps.get_model('pages', 'ServiceDetailPage')
    BrandingSettings = apps.get_model('pages', 'BrandingSettings')
    land = ServiceDetailPage.objects.filter(slug='land').first()
    if land:
        for branding in BrandingSettings.objects.all():
            branding.land_plan_services.add(land)


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_brandingsettings_land_plan_services_and_more'),
    ]

    operations = [migrations.RunPython(enable_for_land, migrations.RunPython.noop)]

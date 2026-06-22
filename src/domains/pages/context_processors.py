from django.conf import settings


def site_name(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Real Estate'),
        'RECAPTCHA_SITE_KEY': getattr(settings, 'RECAPTCHA_SITE_KEY', ''),
        'DEBUG': settings.DEBUG,
    }

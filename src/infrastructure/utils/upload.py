from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


def validate_upload_size(file):
    limit = int(settings.MAX_UPLOAD_MB * 1024 * 1024)
    if file.size > limit:
        raise ValidationError(
            'This file is %(size)s, which is too large. Please upload one under %(max)s '
            '(tip: compress or resize it first).',
            params={'size': filesizeformat(file.size), 'max': filesizeformat(limit)},
            code='file_too_large',
        )

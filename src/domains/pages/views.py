import json
import re

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ColorPreset

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


@require_POST
def save_color_preset(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    name = data.get('name', '').strip()
    primary = data.get('primary_color', '').strip()
    secondary = data.get('secondary_color', '').strip()

    if not name:
        return JsonResponse({'status': 'error', 'message': 'Preset name is required'}, status=400)
    if not _HEX_RE.match(primary) or not _HEX_RE.match(secondary):
        return JsonResponse({'status': 'error', 'message': 'Invalid hex color'}, status=400)

    ColorPreset.objects.update_or_create(
        name=name,
        defaults={'primary_color': primary, 'secondary_color': secondary},
    )
    return JsonResponse({'status': 'ok'})

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.views.decorators.http import require_POST
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .forms import image_info
from .models import Currency, ProjectViewSet


class CurrencyViewSet(SnippetViewSet):
    model = Currency
    icon = 'tag'
    add_to_settings_menu = True
    list_display = ['code', 'name', 'symbol']
    search_fields = ['code', 'name']
    ordering = ['code']


register_snippet(CurrencyViewSet)
register_snippet(ProjectViewSet)


@hooks.register('register_admin_urls')
def register_image_info_url():
    return [path('projects/image-info/<int:image_id>/', image_info_view, name='projects_image_info')]


def image_info_view(request, image_id):
    """Rendition URLs for an image the user may choose; lets the land plan editor show a just-picked photo."""
    from wagtail.images.permissions import permission_policy
    images = permission_policy.instances_user_has_permission_for(request.user, 'choose')
    return JsonResponse(image_info(get_object_or_404(images, pk=image_id)))


MAX_AUTOSAVE_BYTES = 600_000


@hooks.register('register_admin_urls')
def register_land_plan_autosave_url():
    return [path('projects/<int:project_id>/land-plan/', land_plan_autosave, name='projects_land_plan_autosave')]


@require_POST
def land_plan_autosave(request, project_id):
    """Background save for the land plan editor: one full snapshot (state + undo/redo history) per request.

    Safe to retry. The write only applies if `base_rev` is still the current revision (a single atomic UPDATE),
    so a late or duplicate request can never overwrite newer data. On a mismatch we answer 409 with what is
    stored; `writer` tells the client whether that was its own earlier request or another tab/user.
    """
    from django.core.exceptions import ValidationError

    from .models import Project, _clean_annotations, _clean_history, PHOTO_SLOTS

    if not request.user.has_perm('projects.change_project'):
        return JsonResponse({'error': 'You do not have permission to edit projects.'}, status=403)
    if len(request.body) > MAX_AUTOSAVE_BYTES:
        return JsonResponse({'error': 'Too much annotation data.'}, status=413)
    try:
        body = json.loads(request.body)
        client_id, base_rev = str(body['client_id'])[:40], int(body['base_rev'])
        state, history = body['state'], body.get('history', {})
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'error': 'Malformed request.'}, status=400)

    project = get_object_or_404(Project, pk=project_id)
    if not project.is_land:
        return JsonResponse({'code': 'not_enabled', 'error': 'Land plan annotations are not enabled for this project\'s service. '
                                                             'Save the project with a land service first.'}, status=422)
    available = [s for s in PHOTO_SLOTS if getattr(project, f'{s}_id')]
    # Photos picked in the form but not saved yet can't be stored; tell the client instead of dropping them silently.
    dropped = [s for s in (state.get('photos') or {}) if s in PHOTO_SLOTS and s not in available] if isinstance(state, dict) else []
    try:
        cleaned = _clean_annotations(state, available)
    except ValidationError as e:
        return JsonResponse({'code': 'invalid', 'error': ' '.join(e.messages)}, status=422)
    saved_history = dict(_clean_history(history), writer=client_id)

    updated = Project.objects.filter(pk=project_id, land_plan_rev=base_rev).update(
        land_plan_annotations=cleaned, land_plan_history=saved_history, land_plan_rev=base_rev + 1,
    )
    if updated:
        return JsonResponse({'rev': base_rev + 1, 'dropped': dropped})
    current = Project.objects.get(pk=project_id)
    return JsonResponse({
        'rev': current.land_plan_rev, 'writer': (current.land_plan_history or {}).get('writer', ''),
        'state': current.land_plan_annotations, 'history': current.land_plan_history,
    }, status=409)

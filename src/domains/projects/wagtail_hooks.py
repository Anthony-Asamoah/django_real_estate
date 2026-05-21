from wagtail.snippets.models import register_snippet

from .models import ProjectViewSet

register_snippet(ProjectViewSet)

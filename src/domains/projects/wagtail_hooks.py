from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Currency, ProjectViewSet


class CurrencyViewSet(SnippetViewSet):
    model = Currency
    icon = 'tag'
    list_display = ['code', 'name', 'symbol']
    search_fields = ['code', 'name']
    ordering = ['code']


register_snippet(CurrencyViewSet)
register_snippet(ProjectViewSet)

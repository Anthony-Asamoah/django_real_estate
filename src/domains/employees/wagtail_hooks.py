from wagtail.snippets.views.snippets import SnippetViewSet

from infrastructure.utils.list_filters import KeepListFiltersViewSetMixin

from .models import Employee


class EmployeeViewSet(KeepListFiltersViewSetMixin, SnippetViewSet):
    model = Employee
    icon = 'user'

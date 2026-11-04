from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Employee


class EmployeeViewSet(SnippetViewSet):
    model = Employee
    icon = 'user'

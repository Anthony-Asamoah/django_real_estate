from urllib.parse import urlsplit

from django.urls import reverse
from wagtail.snippets.views.snippets import CreateView, EditView

SESSION_KEY = 'projects_list_query'


class KeepListFiltersMixin:
    """After saving, return to the Projects list with the filters, search, sort and page it had.

    Wagtail redirects to the plain list URL. The list keeps its state in the query string, and a click on a project sends
    that URL as the Referer, so we remember it when the edit/add page is opened and re-apply it after the save.
    """

    def get(self, request, *args, **kwargs):
        ref = urlsplit(request.META.get('HTTP_REFERER', ''))
        same_site = not ref.netloc or ref.netloc == request.get_host()   # ignore a Referer from another site
        if same_site and ref.path == reverse(self.index_url_name):
            request.session[SESSION_KEY] = ref.query
        elif ref.path != request.path:   # arrived from anywhere else (menu, dashboard, bookmark): no filters to restore
            request.session.pop(SESSION_KEY, None)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        url = super().get_success_url()
        query = self.request.session.get(SESSION_KEY, '')
        return f'{url}?{query}' if query else url


class ProjectEditView(KeepListFiltersMixin, EditView):
    pass


class ProjectCreateView(KeepListFiltersMixin, CreateView):
    pass

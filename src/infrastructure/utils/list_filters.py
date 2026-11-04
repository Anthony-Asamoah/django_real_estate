"""Return to an admin list with its filters, search, sort and page intact.

Wagtail sends you back to the plain list after a save or delete, and its "back to the list" breadcrumb does the same.
A list keeps its state in the query string, and clicking an item sends that URL as the Referer, so we remember it when
an item's edit/add/delete/view page opens and re-apply it to those redirects and breadcrumb links.
"""
from urllib.parse import urlsplit

from django.urls import reverse
from wagtail.snippets.views.snippets import CreateView, DeleteView, EditView, InspectView


class KeepListFiltersMixin:
    def _session_key(self):
        return f'list_query:{self.index_url_name}'   # one remembered state per list

    def _with_query(self, url):
        query = self.request.session.get(self._session_key(), '')
        return f'{url}?{query}' if query and url == reverse(self.index_url_name) else url   # only the plain list URL

    def get(self, request, *args, **kwargs):
        index = reverse(self.index_url_name)
        ref = urlsplit(request.META.get('HTTP_REFERER', ''))
        ours = not ref.netloc or ref.netloc == request.get_host()   # a Referer from another site counts as "from elsewhere"
        if ours and ref.path == index:
            request.session[self._session_key()] = ref.query
        elif not (ours and ref.path.startswith(index)):   # not from this list or one of its item pages: nothing to restore
            request.session.pop(self._session_key(), None)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self._with_query(super().get_success_url())

    def get_breadcrumbs_items(self):
        return [dict(item, url=self._with_query(item['url'])) if item.get('url') else item for item in super().get_breadcrumbs_items()]


class KeepFiltersEditView(KeepListFiltersMixin, EditView):
    pass


class KeepFiltersCreateView(KeepListFiltersMixin, CreateView):
    pass


class KeepFiltersDeleteView(KeepListFiltersMixin, DeleteView):
    pass


class KeepFiltersInspectView(KeepListFiltersMixin, InspectView):
    pass


class KeepListFiltersViewSetMixin:
    """Put first in a SnippetViewSet's bases to give all of its item pages the behaviour above."""
    edit_view_class = KeepFiltersEditView
    add_view_class = KeepFiltersCreateView
    delete_view_class = KeepFiltersDeleteView
    inspect_view_class = KeepFiltersInspectView

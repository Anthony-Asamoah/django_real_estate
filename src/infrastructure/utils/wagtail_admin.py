"""Shared Wagtail admin pieces for visitor-submitted records.

Inquiries and testimonials are records of what a visitor actually submitted, so
the admin should be able to read and triage them but never author or rewrite
them. These panels and the permission policy enforce that.
"""
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel
from wagtail.permission_policies.base import ModelPermissionPolicy
from wagtail.rich_text import expand_db_html
from wagtail.snippets.views.snippets import SnippetViewSet


class ReadOnlyPanel(FieldPanel):
    """A FieldPanel that is always read-only."""

    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        super().__init__(*args, **kwargs)


class ReadOnlyRichTextPanel(ReadOnlyPanel):
    """Read-only panel that renders RichTextField content as HTML.

    Wagtail's read-only output escapes the display value, and its default
    `format_value_for_display` only strips a `RichText` object down to plain
    text — a RichTextField's raw value is a `str`, so it falls through and the
    admin ends up showing literal `<p>` tags. Expanding the stored rich text
    and marking it safe renders the sender's formatting as they wrote it.
    """

    def format_value_for_display(self, value):
        return mark_safe(expand_db_html(value or ''))


class ReadOnlyPermissionPolicy(ModelPermissionPolicy):
    """Denies 'add' outright, for every user including superusers.

    Submissions are records of what a visitor actually sent, so there is no
    such thing as one an admin authored. 'change' stays permitted only so the
    detail page remains reachable — the submitted fields are all `read_only`,
    so a submission to the edit form cannot alter them. 'delete' is left to the
    normal Django permissions so spam can still be cleared out.
    """

    DENIED_ACTIONS = {'add'}

    def user_has_permission(self, user, action):
        if action in self.DENIED_ACTIONS:
            return False
        return super().user_has_permission(user, action)

    def users_with_any_permission(self, actions):
        allowed = set(actions) - self.DENIED_ACTIONS
        if not allowed:
            # An empty codename list would still match superusers via the base
            # class's `Q(is_superuser=True)`, so return an empty set explicitly.
            return get_user_model().objects.none()
        return super().users_with_any_permission(allowed)


class ReadOnlySubmissionViewSet(SnippetViewSet):
    """Snippet admin that can list and view submissions, but not create them."""

    @property
    def permission_policy(self):
        return ReadOnlyPermissionPolicy(self.model)

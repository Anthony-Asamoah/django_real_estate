from django import forms
from django.contrib.auth import get_user_model
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.permission_policies.base import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import GeneralInquiry, ProjectInquiry


_ROW = (
    '<div style="display:flex;align-items:center;gap:.75rem;padding:.55rem .8rem;'
    'background:rgba(255,255,255,.04);border-radius:7px;'
    'border:1px solid rgba(255,255,255,.07);margin-bottom:.45rem">'
    '<a style="flex:1;font-size:.85rem;color:#d6e4f0;text-decoration:none;'
    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis" href="{href}">{label}</a>'
    '<span style="display:inline-block;background:rgba(48,202,160,.15);color:#30caa0;'
    'border:1px solid rgba(48,202,160,.38);border-radius:10px;padding:1px 9px;'
    'font-size:.74rem;font-weight:700;flex-shrink:0;line-height:1.6">{count}</span>'
    '<button type="button" class="unread-mark-btn" data-model="{model}" '
    'style="flex-shrink:0;font-size:.72rem;padding:3px 11px;'
    'border:1px solid rgba(48,202,160,.35);border-radius:5px;'
    'background:rgba(48,202,160,.1);color:#30caa0;cursor:pointer;'
    'white-space:nowrap;line-height:1.5;position:static">'
    'Mark all read</button>'
    '</div>'
)


def _row_html(label, count, model_key, href):
    return _ROW.format(label=label, count=count, model=model_key, href=href)


class UnreadNotificationsPanel:
    order = 5
    media = forms.Media()

    def render_html(self, request):
        from .models import ProjectInquiry, GeneralInquiry
        from domains.pages.models import Testimonial

        pi = ProjectInquiry.objects.filter(is_read=False).count()
        gi = GeneralInquiry.objects.filter(is_read=False).count()
        t = Testimonial.objects.filter(is_read=False).count()
        total = pi + gi + t

        if not total:
            return mark_safe('')

        rows = ''
        if pi:
            rows += _row_html('Project Inquiries', pi, 'project',
                              '/cms/snippets/inquiries/projectinquiry/')
        if gi:
            rows += _row_html('General Inquiries', gi, 'general',
                              '/cms/snippets/inquiries/generalinquiry/')
        if t:
            rows += _row_html('Testimonials', t, 'testimonial',
                              '/cms/snippets/pages/testimonial/')

        return mark_safe(
            f'<section class="unread-notifications-panel" style="'
            f'background:rgba(11,31,58,.8);'
            f'border:1px solid rgba(48,202,160,.35);border-radius:12px;'
            f'padding:1.1rem 1.4rem 1.3rem;margin-bottom:1.5rem;'
            f'box-shadow:0 4px 28px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.05)">'
            f'<div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.9rem">'
            f'<span class="unread-pulse" style="display:inline-block;width:10px;height:10px;'
            f'border-radius:50%;background:#30caa0;flex-shrink:0"></span>'
            f'<h3 style="font-size:.82rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.07em;color:#30caa0;margin:0">New Unread ({total})</h3>'
            f'</div>'
            f'<div>{rows}</div>'
            f'</section>'
        )


@hooks.register('construct_homepage_panels')
def add_notifications_panel(request, panels):
    panels.insert(0, UnreadNotificationsPanel())


class ReadOnlyPermissionPolicy(ModelPermissionPolicy):
    """Denies 'add' outright, for every user including superusers.

    Inquiries are records of what a visitor actually submitted, so there is no
    such thing as one an admin authored. 'change' stays permitted only so the
    detail page remains reachable — every panel on these models is
    `read_only`, which leaves the edit form with no writable fields, so a
    submission to it cannot alter the record. 'delete' is left to the normal
    Django permissions so spam can still be cleared out.
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


class ReadOnlyInquiryViewSet(SnippetViewSet):
    """Snippet admin that can list and view inquiries, but not create them."""

    @property
    def permission_policy(self):
        return ReadOnlyPermissionPolicy(self.model)


class ProjectInquiryViewSet(ReadOnlyInquiryViewSet):
    model = ProjectInquiry
    list_display = ['name', 'listing', 'email', 'phone', 'timestamp', 'is_read']


class GeneralInquiryViewSet(ReadOnlyInquiryViewSet):
    model = GeneralInquiry
    list_display = ['name', 'service', 'email', 'phone', 'timestamp', 'is_read']


register_snippet(ProjectInquiryViewSet)
register_snippet(GeneralInquiryViewSet)


@hooks.register('register_admin_urls')
def register_notification_urls():
    from . import views
    return [
        path('notifications/mark-read/', views.mark_read, name='mark_read'),
        path('notifications/counts/', views.notification_counts, name='notification_counts'),
    ]

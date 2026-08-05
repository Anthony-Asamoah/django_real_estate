from django.templatetags.static import static
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import ngettext
from wagtail import hooks
from wagtail.snippets.bulk_actions.snippet_bulk_action import SnippetBulkAction
from wagtail.snippets.models import register_snippet
from wagtail.snippets.permissions import get_permission_name

from infrastructure.utils.wagtail_admin import ReadOnlySubmissionViewSet
from .models import Testimonial


class TestimonialViewSet(ReadOnlySubmissionViewSet):
    model = Testimonial
    list_display = ['author_name', 'author_role', 'service', 'is_featured', 'created_at', 'is_read']
    list_filter = ['is_featured', 'is_read']


register_snippet(TestimonialViewSet)


class _FeatureBulkActionBase(SnippetBulkAction):
    """Shared behaviour for the feature/unfeature listing actions.

    `is_featured` is what puts a testimonial in front of visitors — the
    testimonials block only renders featured ones — so publishing is done here
    rather than by editing the (read-only) record.
    """

    models = [Testimonial]
    template_name = 'wagtailsnippets/bulk_actions/confirm_bulk_feature.html'
    is_featured = True

    def check_perm(self, obj):
        return self.request.user.has_perm(get_permission_name('change', self.model))

    def get_execution_context(self):
        return {**super().get_execution_context(), 'is_featured': self.is_featured}

    @classmethod
    def execute_action(cls, objects, is_featured=True, **kwargs):
        model = kwargs['self'].model
        updated = model.objects.filter(pk__in=[obj.pk for obj in objects]).update(
            is_featured=is_featured
        )
        return updated, 0

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            action_verb=self.action_verb,
            confirm_prompt=self.confirm_prompt,
            **kwargs,
        )


class FeatureBulkAction(_FeatureBulkActionBase):
    display_name = 'Show on website'
    aria_label = 'Show selected testimonials on the website'
    action_type = 'feature_testimonial'
    action_priority = 10
    is_featured = True
    action_verb = 'Show on website'
    confirm_prompt = 'These testimonials will be shown on the website:'

    def get_success_message(self, num_parent_objects, num_child_objects):
        return ngettext(
            '%(count)d testimonial is now shown on the website',
            '%(count)d testimonials are now shown on the website',
            num_parent_objects,
        ) % {'count': num_parent_objects}


class UnfeatureBulkAction(_FeatureBulkActionBase):
    display_name = 'Hide from website'
    aria_label = 'Hide selected testimonials from the website'
    action_type = 'unfeature_testimonial'
    action_priority = 11
    is_featured = False
    action_verb = 'Hide from website'
    confirm_prompt = 'These testimonials will be hidden from the website:'

    def get_success_message(self, num_parent_objects, num_child_objects):
        return ngettext(
            '%(count)d testimonial is no longer shown on the website',
            '%(count)d testimonials are no longer shown on the website',
            num_parent_objects,
        ) % {'count': num_parent_objects}


# `register_bulk_action` registers the class itself, not a callable returning it.
hooks.register('register_bulk_action', FeatureBulkAction)
hooks.register('register_bulk_action', UnfeatureBulkAction)


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static('css/wagtail_admin.css'))


@hooks.register('insert_global_admin_js')
def global_admin_fa():
    return format_html(
        '<script src="https://kit.fontawesome.com/2399d93fcf.js" crossorigin="anonymous"></script>'
    )


@hooks.register('insert_global_admin_js')
def branding_admin_js():
    return format_html('<script src="{}"></script>', static('js/admin_branding.js'))


@hooks.register('insert_global_admin_js')
def notifications_admin_js():
    return format_html('<script src="{}"></script>', static('js/admin_notifications.js'))


@hooks.register('register_admin_urls')
def register_branding_admin_urls():
    from . import views
    return [
        path('branding-preset/save/', views.save_color_preset, name='save_color_preset'),
    ]

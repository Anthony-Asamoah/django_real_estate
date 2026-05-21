from django.templatetags.static import static
from django.urls import path
from django.utils.html import format_html
from wagtail import hooks


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


@hooks.register('register_admin_urls')
def register_branding_admin_urls():
    from . import views
    return [
        path('branding-preset/save/', views.save_color_preset, name='save_color_preset'),
    ]

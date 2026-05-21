from django.templatetags.static import static
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

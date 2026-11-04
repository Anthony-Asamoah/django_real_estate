from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views


@hooks.register('register_admin_urls')
def register_manual_urls():
    return [
        path('manual/', views.manual, name='manual'),
        path('manual/<slug:slug>/', views.manual, name='manual_section'),
    ]


@hooks.register('register_help_menu_item')
def register_manual_menu_item():
    return MenuItem('User Manual', reverse_lazy('manual'), icon_name='doc-full', order=1000)

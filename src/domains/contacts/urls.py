from django.urls import path

from domains.contacts import views

app_name = 'contact'
urlpatterns = [
    path('contact', views.contact, name='contact'),
    path('contact/inquiry/', views.general_inquiry, name='general_inquiry'),
]

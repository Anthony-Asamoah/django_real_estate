from django.urls import path

from domains.inquiries import views

app_name = 'inquiry'
urlpatterns = [
    path('contact', views.contact, name='contact'),
    path('contact/inquiry/', views.general_inquiry, name='general_inquiry'),
    path('testimonial/', views.testimonial_submission, name='testimonial_submission'),
]

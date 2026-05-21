from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.index, name='projects'),
    path('<int:project_id>', views.project, name='project'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list_view, name='project_list'),
    path('create/', views.project_create_view, name='project_create'),
    path('<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('<int:project_id>/edit/', views.project_edit_view, name='project_edit'),
]

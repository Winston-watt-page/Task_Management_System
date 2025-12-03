from django.urls import path
from . import web_views

urlpatterns = [
    # Authentication
    path('', web_views.login_page, name='login'),
    path('login/', web_views.login_page, name='login'),
    path('register/', web_views.register_page, name='register'),
    path('logout/', web_views.logout_page, name='logout'),
    
    # Dashboard
    path('dashboard/', web_views.dashboard, name='dashboard'),
    
    # Projects
    path('projects/', web_views.project_list, name='project_list'),
    path('projects/<int:pk>/', web_views.project_detail, name='project_detail'),
    path('projects/create/', web_views.project_create, name='project_create'),
    path('projects/<int:pk>/update/', web_views.project_update, name='project_update'),
    
    # Sprints
    path('sprints/', web_views.sprint_list, name='sprint_list'),
    path('sprints/<int:pk>/', web_views.sprint_detail, name='sprint_detail'),
    path('projects/<int:project_pk>/sprints/create/', web_views.sprint_create, name='sprint_create'),
    
    # Tasks
    path('tasks/', web_views.task_list, name='task_list'),
    path('tasks/<int:pk>/', web_views.task_detail, name='task_detail'),
    path('tasks/create/', web_views.task_create, name='task_create'),
    path('tasks/<int:pk>/update/', web_views.task_update, name='task_update'),
    
    # Reviews
    path('reviews/', web_views.review_list, name='review_list'),
    path('reviews/<int:pk>/', web_views.review_detail, name='review_detail'),
    path('tasks/<int:task_pk>/reviews/create/', web_views.review_create, name='review_create'),
    
    # Notifications
    path('notifications/', web_views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', web_views.notification_mark_read, name='notification_mark_read'),
]

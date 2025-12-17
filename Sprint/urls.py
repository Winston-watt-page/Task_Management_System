from django.urls import path
from . import views

urlpatterns = [
    # Sprint URLs
    path('sprints/', views.sprint_list_view, name='sprint_list'),
    path('sprints/create/', views.sprint_create_view, name='sprint_create'),
    path('sprints/<int:sprint_id>/', views.sprint_detail_view, name='sprint_detail'),
    path('sprints/<int:sprint_id>/start/', views.sprint_start_view, name='sprint_start'),
    path('sprints/<int:sprint_id>/complete/', views.sprint_complete_view, name='sprint_complete'),
    
    # Issue URLs
    path('issues/', views.issue_list_view, name='issue_list'),
    path('issues/my/', views.my_issues_view, name='my_issues'),
    path('issues/create/', views.issue_create_view, name='issue_create'),
    path('issues/<int:issue_id>/', views.issue_detail_view, name='issue_detail'),
    path('issues/<int:issue_id>/update-status/', views.issue_update_status_view, name='issue_update_status'),
    path('issues/<int:issue_id>/update-due-date/', views.issue_update_due_date_view, name='issue_update_due_date'),
    path('issues/<int:issue_id>/comment/', views.issue_add_comment_view, name='issue_add_comment'),
    path('issues/<int:issue_id>/log-time/', views.issue_log_time_view, name='issue_log_time'),
]

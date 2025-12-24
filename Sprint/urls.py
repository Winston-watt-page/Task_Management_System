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
    
    # Code Review URLs
    path('code-review/', views.code_review_dashboard, name='code_review_dashboard'),
    path('code-review/<int:issue_id>/assign/', views.assign_code_reviewer, name='assign_code_reviewer'),
    path('code-review/<int:issue_id>/complete/', views.complete_code_review, name='complete_code_review'),
    path('code-review/sprint/<int:sprint_id>/assign/', views.assign_sprint_code_reviewer, name='assign_sprint_code_reviewer'),
    path('code-review/sprint/<int:sprint_id>/complete/', views.complete_sprint_code_review, name='complete_sprint_code_review'),
    
    # Testing URLs
    path('testing/', views.testing_dashboard, name='testing_dashboard'),
    path('testing/<int:issue_id>/assign/', views.assign_tester, name='assign_tester'),
    path('testing/<int:issue_id>/complete/', views.complete_testing, name='complete_testing'),
    path('testing/sprint/<int:sprint_id>/assign/', views.assign_sprint_tester, name='assign_sprint_tester'),
    path('testing/sprint/<int:sprint_id>/complete/', views.complete_sprint_testing, name='complete_sprint_testing'),
    
    # Notification URLs
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),
    path('notifications/json/', views.get_notifications_json, name='get_notifications_json'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    register_view, login_view, logout_view,
    UserViewSet, TeamViewSet, TeamMemberViewSet, ProjectViewSet, ProjectMemberViewSet,
    SprintViewSet, TaskViewSet, TaskDependencyViewSet, ReviewViewSet,
    ReviewCommentViewSet, CommentViewSet, MentionViewSet, AttachmentViewSet,
    NotificationViewSet, ActivityLogViewSet, ReportViewSet, AnalyticsViewSet,
    project_statistics, sprint_statistics, task_statistics, employee_performance
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'team-members', TeamMemberViewSet, basename='teammember')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-members', ProjectMemberViewSet, basename='projectmember')
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'task-dependencies', TaskDependencyViewSet, basename='taskdependency')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'review-comments', ReviewCommentViewSet, basename='reviewcomment')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'mentions', MentionViewSet, basename='mention')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'activity-logs', ActivityLogViewSet, basename='activitylog')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # Authentication
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Analytics and Reporting
    path('analytics/projects/', project_statistics, name='project-statistics'),
    path('analytics/sprints/', sprint_statistics, name='sprint-statistics'),
    path('analytics/tasks/', task_statistics, name='task-statistics'),
    path('analytics/employee-performance/', employee_performance, name='employee-performance'),
    
    # Router URLs
    path('', include(router.urls)),
]

from django.contrib import admin
from .models import (
    User, Team, TeamMember, Project, ProjectMember, Sprint, Task, TaskDependency,
    Review, ReviewComment, Comment, Mention, Attachment, Notification, ActivityLog,
    Report, Analytics
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_leader', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'status', 'progress_percentage', 'start_date', 'end_date']
    list_filter = ['status', 'team', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'role', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['project__name', 'user__username']
    ordering = ['-assigned_at']


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'start_date', 'end_date', 'velocity']
    list_filter = ['status', 'project', 'start_date']
    search_fields = ['name', 'goal']
    ordering = ['-start_date']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'sprint', 'assigned_to', 'priority', 'status', 'due_date']
    list_filter = ['status', 'priority', 'project', 'sprint', 'created_at']
    search_fields = ['title', 'description', 'tags']
    ordering = ['-created_at']


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['task', 'depends_on_task', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['task__title', 'depends_on_task__title']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['task', 'submitted_by', 'reviewer', 'status', 'rating', 'submitted_at']
    list_filter = ['status', 'rating', 'submitted_at']
    search_fields = ['task__title', 'submitted_by__username', 'reviewer__username']
    ordering = ['-submitted_at']


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__task__title', 'user__username', 'comment']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'parent_comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__title', 'user__username', 'content']
    ordering = ['-created_at']


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'comment__content']
    ordering = ['-created_at']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'file_name', 'uploaded_by', 'file_size', 'version', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['task__title', 'file_name', 'uploaded_by__username']
    ordering = ['-uploaded_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    ordering = ['-created_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'entity_type', 'entity_id', 'action', 'created_at']
    list_filter = ['entity_type', 'action', 'created_at']
    search_fields = ['user__username', 'entity_type', 'entity_id']
    ordering = ['-created_at']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['team__name', 'user__username']
    ordering = ['-joined_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'generated_by', 'format', 'generated_at']
    list_filter = ['type', 'format', 'generated_at']
    search_fields = ['name', 'generated_by__username']
    ordering = ['-generated_at']


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ['project', 'sprint', 'date', 'total_tasks', 'completed_tasks', 'completion_rate', 'velocity']
    list_filter = ['date', 'project', 'sprint']
    search_fields = ['project__name', 'sprint__name']
    ordering = ['-date']

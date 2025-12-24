from django.contrib import admin
from .models import Sprint, Issue, Comment, Notification, Attachment, ActivityLog, TimeLog, Watcher

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'team_lead', 'start_date', 'end_date')
    list_filter = ('status', 'project')
    search_fields = ('name', 'project__name')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'project', 'issue_type', 'priority', 'status', 'assignee', 'code_review_status', 'testing_status')
    list_filter = ('status', 'priority', 'issue_type', 'code_review_status', 'testing_status', 'project')
    search_fields = ('title', 'description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user', 'created_at')
    list_filter = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message')

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'issue', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')

@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user', 'hours_spent', 'date')
    list_filter = ('date',)

@admin.register(Watcher)
class WatcherAdmin(admin.ModelAdmin):
    list_display = ('issue', 'user', 'created_at')
    list_filter = ('created_at',)

from django.db import models
from django.contrib.auth.models import User
from Projects.models import Project

class Sprint(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=200)
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lead_sprints', help_text="TL assigned to this sprint")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_sprints', help_text="User assigned to work on this sprint")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    goal = models.TextField(blank=True, null=True, help_text="Sprint goal/objective")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    velocity = models.IntegerField(default=0, help_text="Story points completed")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sprints')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.key} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'

class Issue(models.Model):
    ISSUE_TYPE_CHOICES = [
        ('story', 'Story'),
        ('task', 'Task'),
        ('bug', 'Bug'),
        ('epic', 'Epic'),
        ('subtask', 'Subtask'),
    ]
    
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    epic = models.ForeignKey('Projects.Epic', on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks', help_text="Parent issue for subtasks")
    
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES, default='task')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    story_points = models.IntegerField(null=True, blank=True, help_text="Estimation in story points")
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Estimated hours")
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Actual hours spent")
    
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_issues')
    due_date = models.DateField(null=True, blank=True)
    
    labels = models.ManyToManyField('Projects.Label', blank=True, related_name='issues')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.key}-{self.id}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'

class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.issue}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

class Attachment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} - {self.issue}"
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('commented', 'Commented'),
        ('assigned', 'Assigned'),
        ('attached', 'Attachment Added'),
    ]
    
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    field_changed = models.CharField(max_length=100, blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.issue}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

class TimeLog(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.hours_spent}h on {self.issue}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'

class Watcher(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='watchers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} watching {self.issue}"
    
    class Meta:
        unique_together = ['issue', 'user']
        ordering = ['-created_at']
        verbose_name = 'Watcher'
        verbose_name_plural = 'Watchers'

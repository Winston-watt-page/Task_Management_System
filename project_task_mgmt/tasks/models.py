from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEAM_LEADER', 'Team Leader'),
        ('EMPLOYEE', 'Employee'),
        ('REVIEWER', 'Reviewer'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_team_leader(self):
        return self.role == 'TEAM_LEADER'
    
    @property
    def is_employee(self):
        return self.role in ['EMPLOYEE', 'TEAM_LEADER']
    
    @property
    def is_reviewer(self):
        return self.role == 'REVIEWER'


class Team(models.Model):
    """Team model for organizing users"""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    team_leader = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='led_teams'
    )
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Team members with specific roles - additional metadata for team membership"""
    
    ROLE_CHOICES = [
        ('DEVELOPER', 'Developer'),
        ('TESTER', 'Tester'),
        ('DESIGNER', 'Designer'),
        ('ANALYST', 'Analyst'),
        ('DEVOPS', 'DevOps'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_member_roles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEVELOPER')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_members'
        unique_together = ['team', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"


class Project(models.Model):
    """Project model for managing projects"""
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_projects')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def calculate_progress(self):
        """Calculate project progress based on completed tasks"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='DONE').count()
        return int((completed_tasks / total_tasks) * 100)
    
    def save(self, *args, **kwargs):
        # Always recalculate progress
        if self.pk:
            self.progress_percentage = self.calculate_progress()
        super().save(*args, **kwargs)
    
    def update_progress(self):
        """Update project progress and save"""
        self.progress_percentage = self.calculate_progress()
        self.save(update_fields=['progress_percentage', 'updated_at'])


class ProjectMember(models.Model):
    """Project members with specific roles"""
    
    ROLE_CHOICES = [
        ('PROJECT_MANAGER', 'Project Manager'),
        ('DEVELOPER', 'Developer'),
        ('TESTER', 'Tester'),
        ('REVIEWER', 'Reviewer'),
        ('OBSERVER', 'Observer'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DEVELOPER')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_members'
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class Sprint(models.Model):
    """Sprint model for agile project management"""
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=255)
    goal = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    velocity = models.IntegerField(default=0)
    capacity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sprints'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def calculate_velocity(self):
        """Calculate sprint velocity based on completed tasks"""
        completed_tasks = self.tasks.filter(status='DONE')
        return sum(task.estimated_hours for task in completed_tasks)


class Task(models.Model):
    """Task model for individual work items"""
    
    PRIORITY_CHOICES = [
        ('P0', 'P0 - Critical'),
        ('P1', 'P1 - High'),
        ('P2', 'P2 - Medium'),
        ('P3', 'P3 - Low'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('IN_REVIEW', 'In Review'),
        ('DONE', 'Done'),
        ('BLOCKED', 'Blocked'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True,
        blank=True
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='created_tasks'
    )
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='P2')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    estimated_hours = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    actual_hours = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    due_date = models.DateField(blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['DONE', 'CANCELLED']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update project progress when task is saved
        if self.project:
            self.project.update_progress()


class TaskDependency(models.Model):
    """Task dependencies to manage task relationships"""
    
    TYPE_CHOICES = [
        ('FINISH_TO_START', 'Finish to Start'),
        ('START_TO_START', 'Start to Start'),
        ('FINISH_TO_FINISH', 'Finish to Finish'),
        ('START_TO_FINISH', 'Start to Finish'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependencies')
    depends_on_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='dependent_tasks')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='FINISH_TO_START')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_dependencies'
        unique_together = ['task', 'depends_on_task']
    
    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on_task.title}"
    
    def clean(self):
        """Validate no circular dependencies"""
        from django.core.exceptions import ValidationError
        
        # Check self-dependency
        if self.task == self.depends_on_task:
            raise ValidationError("A task cannot depend on itself.")
        
        # Check circular dependency
        if self._has_circular_dependency():
            raise ValidationError("This dependency would create a circular reference.")
    
    def _has_circular_dependency(self):
        """Check if adding this dependency would create a circular reference"""
        visited = set()
        stack = [self.depends_on_task]
        
        while stack:
            current_task = stack.pop()
            if current_task == self.task:
                return True
            
            if current_task.id in visited:
                continue
            
            visited.add(current_task.id)
            
            # Get all tasks that current_task depends on
            dependencies = TaskDependency.objects.filter(task=current_task).select_related('depends_on_task')
            for dep in dependencies:
                if dep.depends_on_task.id not in visited:
                    stack.append(dep.depends_on_task)
        
        return False
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    """Review model for task review management"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_REVIEW', 'In Review'),
        ('APPROVED', 'Approved'),
        ('CHANGES_REQUESTED', 'Changes Requested'),
        ('REJECTED', 'Rejected'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reviews')
    submitted_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='submitted_reviews')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_reviews',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    comments = models.TextField(blank=True)
    rating = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    screenshot = models.ImageField(upload_to='reviews/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Review for {self.task.title} by {self.submitted_by.username}"


class ReviewComment(models.Model):
    """Comments on reviews"""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'review_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.review}"


class Comment(models.Model):
    """Comments on tasks for collaboration"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"
    
    @property
    def mentions(self):
        """Extract @mentions from content"""
        import re
        return re.findall(r'@(\w+)', self.content)


class Mention(models.Model):
    """Track user mentions in comments"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='mentioned_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mentions'
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"@{self.user.username} mentioned in comment"


class Attachment(models.Model):
    """File attachments for tasks"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='uploaded_files')
    file = models.FileField(upload_to='attachments/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)
    file_size = models.BigIntegerField()
    version = models.IntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} (v{self.version})"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Notification system for real-time alerts"""
    
    TYPE_CHOICES = [
        ('TASK_ASSIGNED', 'Task Assigned'),
        ('TASK_UPDATED', 'Task Updated'),
        ('REVIEW_REQUESTED', 'Review Requested'),
        ('REVIEW_COMPLETED', 'Review Completed'),
        ('COMMENT_ADDED', 'Comment Added'),
        ('MENTION', 'Mention'),
        ('SPRINT_STARTED', 'Sprint Started'),
        ('SPRINT_COMPLETED', 'Sprint Completed'),
        ('DEADLINE_APPROACHING', 'Deadline Approaching'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    reference_id = models.CharField(max_length=100, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.type} - {self.user.username}"


class ActivityLog(models.Model):
    """Activity log for audit trail"""
    
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('DELETED', 'Deleted'),
        ('ASSIGNED', 'Assigned'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('COMMENTED', 'Commented'),
        ('REVIEWED', 'Reviewed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.entity_type}"


class Report(models.Model):
    """Reports for analytics and insights"""
    
    TYPE_CHOICES = [
        ('PROJECT_PROGRESS', 'Project Progress'),
        ('SPRINT_METRICS', 'Sprint Metrics'),
        ('EMPLOYEE_PERFORMANCE', 'Employee Performance'),
        ('TEAM_VELOCITY', 'Team Velocity'),
        ('TASK_COMPLETION', 'Task Completion'),
        ('PRODUCTIVITY_SUMMARY', 'Productivity Summary'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    generated_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='generated_reports')
    data = models.JSONField()
    format = models.CharField(max_length=20, default='PDF')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['generated_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"


class Analytics(models.Model):
    """Analytics data for projects and sprints"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='analytics',
        null=True,
        blank=True
    )
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='analytics',
        null=True,
        blank=True
    )
    date = models.DateField()
    total_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    in_progress_tasks = models.IntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    velocity = models.IntegerField(default=0)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['project', 'date']),
            models.Index(fields=['sprint', 'date']),
        ]
    
    def __str__(self):
        if self.project:
            return f"Analytics for {self.project.name} on {self.date}"
        elif self.sprint:
            return f"Analytics for {self.sprint.name} on {self.date}"
        return f"Analytics on {self.date}"

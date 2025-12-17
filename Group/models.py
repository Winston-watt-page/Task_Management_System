from django.db import models
from django.contrib.auth.models import User, Group, Permission

# Note: Django's built-in Group model will be used for role management
# Groups: Admin, TL, Scrum Master, Developer, Tester

class GroupPermissionProfile(models.Model):
    """
    Additional configuration for groups beyond Django's default permissions
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='permission_profile')
    description = models.TextField(blank=True, null=True)
    can_create_projects = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_create_sprints = models.BooleanField(default=False)
    can_start_sprints = models.BooleanField(default=False)
    can_assign_tasks = models.BooleanField(default=False)
    can_update_any_task = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.group.name} Permission Profile"
    
    class Meta:
        verbose_name = 'Group Permission Profile'
        verbose_name_plural = 'Group Permission Profiles'

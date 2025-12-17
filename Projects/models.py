from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('on_hold', 'On Hold'),
    ]
    
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=10, unique=True, help_text="Short key for project (e.g., PROJ)")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"{self.key} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

class Epic(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='epics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_epics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.key} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Epic'
        verbose_name_plural = 'Epics'

class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#0052CC', help_text="Hex color code")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = ['name', 'project']
        ordering = ['name']
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'

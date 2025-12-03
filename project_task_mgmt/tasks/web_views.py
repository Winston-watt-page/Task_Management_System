from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    User, Team, Project, Sprint, Task, Review, Comment,
    Attachment, Notification
)
from .forms import (
    UserRegistrationForm, UserLoginForm, ProjectForm, SprintForm,
    TaskForm, ReviewForm, CommentForm
)


# Authentication Views

def login_page(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'tasks/auth/login.html', {'form': form})


def register_page(request):
    """Registration page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'tasks/auth/register.html', {'form': form})


@login_required
def logout_page(request):
    """Logout"""
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# Dashboard

@login_required
def dashboard(request):
    """Main dashboard"""
    user = request.user
    
    # Get user statistics
    my_tasks = Task.objects.filter(assigned_to=user)
    my_projects = Project.objects.filter(
        Q(team__members=user) | Q(members__user=user)
    ).distinct()
    
    recent_tasks = my_tasks.order_by('-updated_at')[:5]
    pending_reviews = Review.objects.filter(reviewer=user, status='IN_REVIEW')[:5]
    unread_notifications = Notification.objects.filter(user=user, is_read=False)[:5]
    
    context = {
        'total_tasks': my_tasks.count(),
        'open_tasks': my_tasks.filter(status='OPEN').count(),
        'in_progress_tasks': my_tasks.filter(status='IN_PROGRESS').count(),
        'completed_tasks': my_tasks.filter(status='DONE').count(),
        'total_projects': my_projects.count(),
        'pending_reviews_count': pending_reviews.count(),
        'recent_tasks': recent_tasks,
        'pending_reviews': pending_reviews,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'tasks/dashboard.html', context)


# Project Views

@login_required
def project_list(request):
    """List all projects"""
    user = request.user
    
    if user.is_admin:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(team__members=user) | Q(members__user=user)
        ).distinct()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    context = {
        'projects': projects.order_by('-created_at'),
        'status_filter': status_filter,
    }
    
    return render(request, 'tasks/projects/list.html', context)


@login_required
def project_detail(request, pk):
    """Project detail page"""
    project = get_object_or_404(Project, pk=pk)
    sprints = project.sprints.all()
    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'sprints': sprints,
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='DONE').count(),
        'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
    }
    
    return render(request, 'tasks/projects/detail.html', context)


@login_required
def project_create(request):
    """Create new project"""
    if not (request.user.is_admin or request.user.is_team_leader):
        messages.error(request, 'You do not have permission to create projects.')
        return redirect('project_list')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'tasks/projects/form.html', {'form': form, 'action': 'Create'})


@login_required
def project_update(request, pk):
    """Update project"""
    project = get_object_or_404(Project, pk=pk)
    
    if not (request.user.is_admin or request.user.is_team_leader):
        messages.error(request, 'You do not have permission to edit projects.')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'tasks/projects/form.html', {
        'form': form,
        'action': 'Update',
        'project': project
    })


# Sprint Views

@login_required
def sprint_list(request):
    """List all sprints"""
    sprints = Sprint.objects.all().order_by('-start_date')
    
    # Filter by project
    project_id = request.GET.get('project')
    if project_id:
        sprints = sprints.filter(project_id=project_id)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        sprints = sprints.filter(status=status_filter)
    
    context = {
        'sprints': sprints,
        'projects': Project.objects.all(),
    }
    
    return render(request, 'tasks/sprints/list.html', context)


@login_required
def sprint_detail(request, pk):
    """Sprint detail page"""
    sprint = get_object_or_404(Sprint, pk=pk)
    tasks = sprint.tasks.all()
    
    context = {
        'sprint': sprint,
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='DONE').count(),
        'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
    }
    
    return render(request, 'tasks/sprints/detail.html', context)


@login_required
def sprint_create(request, project_pk):
    """Create new sprint"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if not (request.user.is_admin or request.user.is_team_leader):
        messages.error(request, 'You do not have permission to create sprints.')
        return redirect('project_detail', pk=project_pk)
    
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.project = project
            sprint.save()
            messages.success(request, f'Sprint "{sprint.name}" created successfully!')
            return redirect('sprint_detail', pk=sprint.pk)
    else:
        form = SprintForm(initial={'project': project})
    
    return render(request, 'tasks/sprints/form.html', {
        'form': form,
        'action': 'Create',
        'project': project
    })


# Task Views

@login_required
def task_list(request):
    """List all tasks"""
    user = request.user
    
    if user.is_admin or user.is_team_leader:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user)
    
    # Filters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    
    tasks = tasks.order_by('-created_at')
    
    context = {
        'tasks': tasks,
        'projects': Project.objects.all(),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'tasks/tasks/list.html', context)


@login_required
def task_detail(request, pk):
    """Task detail page"""
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.filter(parent_comment=None).order_by('created_at')
    attachments = task.attachments.all()
    reviews = task.reviews.all()
    
    context = {
        'task': task,
        'comments': comments,
        'attachments': attachments,
        'reviews': reviews,
    }
    
    return render(request, 'tasks/tasks/detail.html', context)


@login_required
def task_create(request):
    """Create new task"""
    if not (request.user.is_admin or request.user.is_team_leader):
        messages.error(request, 'You do not have permission to create tasks.')
        return redirect('task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    return render(request, 'tasks/tasks/form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update(request, pk):
    """Update task"""
    task = get_object_or_404(Task, pk=pk)
    
    # Check permissions
    can_edit = (
        request.user.is_admin or
        request.user.is_team_leader or
        task.assigned_to == request.user
    )
    
    if not can_edit:
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_detail', pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', pk=pk)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/tasks/form.html', {
        'form': form,
        'action': 'Update',
        'task': task
    })


# Review Views

@login_required
def review_list(request):
    """List all reviews"""
    user = request.user
    
    if user.is_admin or user.is_team_leader:
        reviews = Review.objects.all()
    elif user.is_reviewer:
        reviews = Review.objects.filter(Q(reviewer=user) | Q(submitted_by=user))
    else:
        reviews = Review.objects.filter(submitted_by=user)
    
    reviews = reviews.order_by('-submitted_at')
    
    context = {
        'reviews': reviews,
    }
    
    return render(request, 'tasks/reviews/list.html', context)


@login_required
def review_detail(request, pk):
    """Review detail page"""
    review = get_object_or_404(Review, pk=pk)
    
    context = {
        'review': review,
    }
    
    return render(request, 'tasks/reviews/detail.html', context)


@login_required
def review_create(request, task_pk):
    """Create new review"""
    task = get_object_or_404(Task, pk=task_pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.task = task
            review.submitted_by = request.user
            review.save()
            
            # Update task status
            task.status = 'IN_REVIEW'
            task.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('review_detail', pk=review.pk)
    else:
        form = ReviewForm()
    
    return render(request, 'tasks/reviews/form.html', {
        'form': form,
        'action': 'Submit',
        'task': task
    })


# Notification Views

@login_required
def notification_list(request):
    """List all notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'tasks/notifications/list.html', context)


@login_required
def notification_mark_read(request, pk):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect('notification_list')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Sprint, Issue, Comment, TimeLog, ActivityLog
from Projects.models import Project

@login_required
def sprint_list_view(request):
    sprints = Sprint.objects.all().select_related('project', 'team_lead')
    return render(request, 'sprint/sprint_list.html', {'sprints': sprints})

@login_required
def sprint_detail_view(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    issues = sprint.issues.all().select_related('assignee', 'reporter')
    
    # Group issues by status
    todo_issues = issues.filter(status='todo')
    in_progress_issues = issues.filter(status='in_progress')
    completed_issues = issues.filter(status='completed')
    
    return render(request, 'sprint/sprint_detail.html', {
        'sprint': sprint,
        'todo_issues': todo_issues,
        'in_progress_issues': in_progress_issues,
        'completed_issues': completed_issues
    })

@login_required
def sprint_create_view(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        name = request.POST.get('name')
        team_lead_id = request.POST.get('team_lead')
        goal = request.POST.get('goal')
        
        project = get_object_or_404(Project, id=project_id)
        team_lead = get_object_or_404(User, id=team_lead_id) if team_lead_id else None
        
        sprint = Sprint.objects.create(
            project=project,
            name=name,
            team_lead=team_lead,
            goal=goal,
            created_by=request.user
        )
        
        messages.success(request, f'Sprint {name} created successfully!')
        return redirect('sprint_detail', sprint_id=sprint.id)
    
    projects = Project.objects.filter(status='active')
    tl_group = User.objects.filter(groups__name='TL')
    return render(request, 'sprint/sprint_create.html', {
        'projects': projects,
        'team_leads': tl_group
    })

@login_required
def sprint_start_view(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    # Check if user is TL of this sprint
    if sprint.team_lead != request.user:
        messages.error(request, 'Only the Team Lead can start this sprint!')
        return redirect('sprint_detail', sprint_id=sprint.id)
    
    if sprint.status != 'planning':
        messages.warning(request, 'Sprint is already started or completed!')
        return redirect('sprint_detail', sprint_id=sprint.id)
    
    sprint.status = 'active'
    sprint.start_date = timezone.now().date()
    sprint.save()
    
    messages.success(request, f'Sprint {sprint.name} started successfully!')
    return redirect('sprint_detail', sprint_id=sprint.id)

@login_required
def sprint_complete_view(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    sprint.status = 'completed'
    sprint.end_date = timezone.now().date()
    sprint.save()
    
    messages.success(request, f'Sprint {sprint.name} completed!')
    return redirect('sprint_detail', sprint_id=sprint.id)

@login_required
def issue_list_view(request):
    issues = Issue.objects.all().select_related('project', 'assignee', 'sprint')
    return render(request, 'sprint/issue_list.html', {'issues': issues})

@login_required
def issue_detail_view(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    comments = issue.comments.all().select_related('user')
    time_logs = issue.time_logs.all().select_related('user')
    activity_logs = issue.activity_logs.all().select_related('user')
    
    return render(request, 'sprint/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'time_logs': time_logs,
        'activity_logs': activity_logs
    })

@login_required
def issue_create_view(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        sprint_id = request.POST.get('sprint')
        title = request.POST.get('title')
        description = request.POST.get('description')
        issue_type = request.POST.get('issue_type')
        priority = request.POST.get('priority')
        assignee_id = request.POST.get('assignee')
        
        project = get_object_or_404(Project, id=project_id)
        sprint = get_object_or_404(Sprint, id=sprint_id) if sprint_id else None
        assignee = get_object_or_404(User, id=assignee_id) if assignee_id else None
        
        issue = Issue.objects.create(
            project=project,
            sprint=sprint,
            title=title,
            description=description,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
            reporter=request.user
        )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='created'
        )
        
        messages.success(request, f'Issue {issue.title} created successfully!')
        return redirect('issue_detail', issue_id=issue.id)
    
    projects = Project.objects.filter(status='active')
    sprints = Sprint.objects.filter(status__in=['planning', 'active'])
    users = User.objects.all()
    
    return render(request, 'sprint/issue_create.html', {
        'projects': projects,
        'sprints': sprints,
        'users': users
    })

@login_required
def issue_update_status_view(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        old_status = issue.status
        new_status = request.POST.get('status')
        
        issue.status = new_status
        issue.save()
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='status_changed',
            field_changed='status',
            old_value=old_status,
            new_value=new_status
        )
        
        messages.success(request, f'Issue status updated to {issue.get_status_display()}!')
        return redirect('issue_detail', issue_id=issue.id)
    
    return redirect('issue_detail', issue_id=issue.id)

@login_required
def issue_add_comment_view(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        Comment.objects.create(
            issue=issue,
            user=request.user,
            content=content
        )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='commented'
        )
        
        messages.success(request, 'Comment added successfully!')
    
    return redirect('issue_detail', issue_id=issue.id)

@login_required
def issue_log_time_view(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        hours_spent = request.POST.get('hours_spent')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        TimeLog.objects.create(
            issue=issue,
            user=request.user,
            hours_spent=hours_spent,
            description=description,
            date=date
        )
        
        # Update actual hours on issue
        issue.actual_hours = float(issue.actual_hours or 0) + float(hours_spent)
        issue.save()
        
        messages.success(request, 'Time logged successfully!')
    
    return redirect('issue_detail', issue_id=issue.id)

@login_required
def my_issues_view(request):
    my_issues = Issue.objects.filter(assignee=request.user).select_related('project', 'sprint')
    return render(request, 'sprint/my_issues.html', {'issues': my_issues})

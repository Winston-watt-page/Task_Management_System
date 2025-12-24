from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import Sprint, Issue, Comment, TimeLog, ActivityLog, Notification
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
        assignee_id = request.POST.get('assignee')
        goal = request.POST.get('goal')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        project = get_object_or_404(Project, id=project_id)
        team_lead = get_object_or_404(User, id=team_lead_id) if team_lead_id else None
        assignee = get_object_or_404(User, id=assignee_id) if assignee_id else None
        
        sprint = Sprint.objects.create(
            project=project,
            name=name,
            team_lead=team_lead,
            assignee=assignee,
            goal=goal,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            created_by=request.user
        )
        
        messages.success(request, f'Sprint {name} created successfully!')
        return redirect('sprint_detail', sprint_id=sprint.id)
    
    projects = Project.objects.filter(status='active')
    tl_group = User.objects.filter(groups__name='TL')
    # Get all users except admin (or get users from Developer/QA groups if they exist)
    developers = User.objects.filter(groups__name__in=['Developer', 'QA']).distinct()
    if not developers.exists():
        # If no users in Developer/QA groups, show all non-superuser users
        developers = User.objects.filter(is_superuser=False, is_active=True)
    return render(request, 'sprint/sprint_create.html', {
        'projects': projects,
        'team_leads': tl_group,
        'developers': developers
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
        
        # Redirect back to sprint if sprint was selected
        if sprint:
            return redirect('sprint_detail', sprint_id=sprint.id)
        else:
            return redirect('issue_detail', issue_id=issue.id)
    
    projects = Project.objects.filter(status='active')
    sprints = Sprint.objects.filter(status__in=['planning', 'active'])
    users = User.objects.filter(groups__name__in=['Developer', 'QA', 'TL'])
    
    # Get pre-selected sprint from query params
    selected_sprint_id = request.GET.get('sprint')
    selected_sprint = None
    if selected_sprint_id:
        selected_sprint = Sprint.objects.filter(id=selected_sprint_id).first()
    
    return render(request, 'sprint/issue_create.html', {
        'projects': projects,
        'sprints': sprints,
        'users': users,
        'selected_sprint': selected_sprint
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
def issue_update_due_date_view(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    # Check if user is the assignee
    if issue.assignee != request.user:
        messages.error(request, 'Only the assignee can set the due date!')
        return redirect('issue_detail', issue_id=issue.id)
    
    if request.method == 'POST':
        due_date = request.POST.get('due_date')
        old_due_date = issue.due_date
        
        issue.due_date = due_date if due_date else None
        issue.save()
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='due_date_changed',
            field_changed='due_date',
            old_value=str(old_due_date) if old_due_date else 'None',
            new_value=str(due_date) if due_date else 'None'
        )
        
        messages.success(request, 'Due date updated successfully!')
    
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


# ===================== CODE REVIEW VIEWS =====================

@login_required
def code_review_dashboard(request):
    """Dashboard for code review tasks"""
    user = request.user
    
    # Check if user is admin or scrum master
    is_admin_or_scrum = user.is_staff or user.groups.filter(name='Scrum Master').exists()
    
    if is_admin_or_scrum:
        # Show all completed issues pending code review
        pending_review = Issue.objects.filter(
            status='completed',
            code_review_status='pending'
        ).select_related('project', 'assignee', 'reporter')
        
        # Show all completed sprints pending code review
        pending_sprint_review = Sprint.objects.filter(
            status='completed',
            code_review_status='pending'
        ).select_related('project', 'team_lead', 'assignee')
        
        # All issues in code review status
        in_review = Issue.objects.filter(
            code_review_status='in_review'
        ).select_related('project', 'assignee', 'code_reviewer')
        
        # All sprints in code review status
        sprints_in_review = Sprint.objects.filter(
            code_review_status='in_review'
        ).select_related('project', 'team_lead', 'code_reviewer')
    else:
        # Regular users see only tasks assigned to them for review
        pending_review = Issue.objects.none()
        pending_sprint_review = Sprint.objects.none()
        in_review = Issue.objects.filter(
            code_reviewer=user,
            code_review_status='in_review'
        ).select_related('project', 'assignee', 'reporter')
        sprints_in_review = Sprint.objects.filter(
            code_reviewer=user,
            code_review_status='in_review'
        ).select_related('project', 'team_lead', 'assignee')
    
    # My review tasks
    my_reviews = Issue.objects.filter(
        code_reviewer=user,
        code_review_status__in=['pending', 'in_review']
    ).select_related('project', 'assignee', 'reporter')
    
    # My sprint reviews
    my_sprint_reviews = Sprint.objects.filter(
        code_reviewer=user,
        code_review_status__in=['pending', 'in_review']
    ).select_related('project', 'team_lead', 'assignee')
    
    # All users for assignment
    users = User.objects.all().exclude(id=user.id)
    
    context = {
        'pending_review': pending_review,
        'pending_sprint_review': pending_sprint_review,
        'in_review': in_review,
        'sprints_in_review': sprints_in_review,
        'my_reviews': my_reviews,
        'my_sprint_reviews': my_sprint_reviews,
        'users': users,
        'is_admin_or_scrum': is_admin_or_scrum,
    }
    
    return render(request, 'sprint/code_review.html', context)


@login_required
def assign_code_reviewer(request, issue_id):
    """Assign a code reviewer to an issue"""
    user = request.user
    
    # Check permissions
    if not (user.is_staff or user.groups.filter(name='Scrum Master').exists()):
        messages.error(request, 'You do not have permission to assign code reviewers.')
        return redirect('code_review_dashboard')
    
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        reviewer_id = request.POST.get('reviewer_id')
        reviewer = get_object_or_404(User, id=reviewer_id)
        
        issue.code_reviewer = reviewer
        issue.code_review_status = 'in_review'
        issue.status = 'code_review'
        issue.save()
        
        # Create notification
        Notification.objects.create(
            recipient=reviewer,
            sender=user,
            notification_type='code_review_assigned',
            issue=issue,
            message=f'{user.username} assigned you to review: {issue.title}'
        )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=user,
            action='assigned',
            field_changed='code_reviewer',
            new_value=reviewer.username
        )
        
        messages.success(request, f'Code reviewer {reviewer.username} assigned successfully.')
        return redirect('code_review_dashboard')
    
    return redirect('code_review_dashboard')


@login_required
def assign_sprint_code_reviewer(request, sprint_id):
    """Assign a code reviewer to a sprint"""
    user = request.user
    
    # Check permissions
    if not (user.is_staff or user.groups.filter(name='Scrum Master').exists()):
        messages.error(request, 'You do not have permission to assign code reviewers.')
        return redirect('code_review_dashboard')
    
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    if request.method == 'POST':
        reviewer_id = request.POST.get('reviewer_id')
        reviewer = get_object_or_404(User, id=reviewer_id)
        
        sprint.code_reviewer = reviewer
        sprint.code_review_status = 'in_review'
        sprint.status = 'code_review'
        sprint.save()
        
        # Create notification
        Notification.objects.create(
            recipient=reviewer,
            sender=user,
            notification_type='code_review_assigned',
            sprint=sprint,
            message=f'{user.username} assigned you to review sprint: {sprint.name}'
        )
        
        messages.success(request, f'Code reviewer {reviewer.username} assigned to sprint successfully.')
        return redirect('code_review_dashboard')
    
    return redirect('code_review_dashboard')


@login_required
def complete_sprint_code_review(request, sprint_id):
    """Mark sprint code review as completed"""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    # Check if user is the assigned reviewer
    if sprint.code_reviewer != request.user:
        messages.error(request, 'You are not assigned to review this sprint.')
        return redirect('code_review_dashboard')
    
    if request.method == 'POST':
        review_status = request.POST.get('review_status')  # 'approved' or 'rejected'
        review_notes = request.POST.get('review_notes', '')
        
        sprint.code_review_status = review_status
        sprint.code_review_completed_at = timezone.now()
        sprint.code_review_notes = review_notes
        
        if review_status == 'approved':
            sprint.status = 'testing'
            sprint.testing_status = 'pending'
            notification_type = 'code_review_approved'
            message = f'Code review approved for sprint: {sprint.name}'
        else:
            sprint.status = 'active'
            notification_type = 'code_review_rejected'
            message = f'Code review rejected for sprint: {sprint.name}. Please fix and resubmit.'
        
        sprint.save()
        
        # Notify admin and scrum masters
        admins_and_scrum = User.objects.filter(Q(is_staff=True) | Q(groups__name='Scrum Master')).distinct()
        
        for admin in admins_and_scrum:
            if admin != request.user:
                Notification.objects.create(
                    recipient=admin,
                    sender=request.user,
                    notification_type=notification_type,
                    sprint=sprint,
                    message=message
                )
        
        # Notify sprint team lead
        if sprint.team_lead and sprint.team_lead != request.user:
            Notification.objects.create(
                recipient=sprint.team_lead,
                sender=request.user,
                notification_type=notification_type,
                sprint=sprint,
                message=message
            )
        
        messages.success(request, f'Sprint code review marked as {review_status}.')
        return redirect('code_review_dashboard')
    
    return redirect('code_review_dashboard')


@login_required
def complete_code_review(request, issue_id):
    """Mark code review as completed"""
    issue = get_object_or_404(Issue, id=issue_id)
    
    # Check if user is the assigned reviewer
    if issue.code_reviewer != request.user:
        messages.error(request, 'You are not assigned to review this issue.')
        return redirect('code_review_dashboard')
    
    if request.method == 'POST':
        review_status = request.POST.get('review_status')  # 'approved' or 'rejected'
        review_notes = request.POST.get('review_notes', '')
        
        issue.code_review_status = review_status
        issue.code_review_completed_at = timezone.now()
        issue.code_review_notes = review_notes
        
        if review_status == 'approved':
            issue.status = 'testing'
            issue.testing_status = 'pending'
            notification_type = 'code_review_approved'
            message = f'Code review approved for: {issue.title}'
        else:
            issue.status = 'in_progress'
            notification_type = 'code_review_rejected'
            message = f'Code review rejected for: {issue.title}. Please fix and resubmit.'
        
        issue.save()
        
        # Notify admin and scrum masters
        admins_and_scrum = User.objects.filter(Q(is_staff=True) | Q(groups__name='Scrum Master')).distinct()
        
        for admin in admins_and_scrum:
            if admin != request.user:
                Notification.objects.create(
                    recipient=admin,
                    sender=request.user,
                    notification_type=notification_type,
                    issue=issue,
                    message=message
                )
        
        # Notify issue owner
        if issue.assignee and issue.assignee != request.user:
            Notification.objects.create(
                recipient=issue.assignee,
                sender=request.user,
                notification_type=notification_type,
                issue=issue,
                message=message
            )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='status_changed',
            field_changed='code_review_status',
            new_value=review_status
        )
        
        messages.success(request, f'Code review marked as {review_status}.')
        return redirect('code_review_dashboard')
    
    return redirect('code_review_dashboard')


# ===================== TESTING VIEWS =====================

@login_required
def testing_dashboard(request):
    """Dashboard for testing tasks"""
    user = request.user
    
    # Check if user is admin or scrum master
    is_admin_or_scrum = user.is_staff or user.groups.filter(name='Scrum Master').exists()
    
    if is_admin_or_scrum:
        # Show all issues approved in code review and pending testing
        pending_testing = Issue.objects.filter(
            code_review_status='approved',
            testing_status='pending'
        ).select_related('project', 'assignee', 'code_reviewer')
        
        # Show all sprints approved in code review and pending testing
        pending_sprint_testing = Sprint.objects.filter(
            code_review_status='approved',
            testing_status='pending'
        ).select_related('project', 'team_lead', 'code_reviewer')
        
        # All issues in testing
        in_testing = Issue.objects.filter(
            testing_status='in_testing'
        ).select_related('project', 'assignee', 'tester')
        
        # All sprints in testing
        sprints_in_testing = Sprint.objects.filter(
            testing_status='in_testing'
        ).select_related('project', 'team_lead', 'tester')
    else:
        # Regular users see only tasks assigned to them for testing
        pending_testing = Issue.objects.none()
        pending_sprint_testing = Sprint.objects.none()
        in_testing = Issue.objects.filter(
            tester=user,
            testing_status='in_testing'
        ).select_related('project', 'assignee', 'code_reviewer')
        sprints_in_testing = Sprint.objects.filter(
            tester=user,
            testing_status='in_testing'
        ).select_related('project', 'team_lead', 'code_reviewer')
    
    # My testing tasks
    my_testing = Issue.objects.filter(
        tester=user,
        testing_status__in=['pending', 'in_testing']
    ).select_related('project', 'assignee', 'code_reviewer')
    
    # My sprint testing tasks
    my_sprint_testing = Sprint.objects.filter(
        tester=user,
        testing_status__in=['pending', 'in_testing']
    ).select_related('project', 'team_lead', 'code_reviewer')
    
    # All users for assignment
    users = User.objects.all().exclude(id=user.id)
    
    context = {
        'pending_testing': pending_testing,
        'pending_sprint_testing': pending_sprint_testing,
        'in_testing': in_testing,
        'sprints_in_testing': sprints_in_testing,
        'my_testing': my_testing,
        'my_sprint_testing': my_sprint_testing,
        'users': users,
        'is_admin_or_scrum': is_admin_or_scrum,
    }
    
    return render(request, 'sprint/testing.html', context)


@login_required
def assign_tester(request, issue_id):
    """Assign a tester to an issue"""
    user = request.user
    
    # Check permissions
    if not (user.is_staff or user.groups.filter(name='Scrum Master').exists()):
        messages.error(request, 'You do not have permission to assign testers.')
        return redirect('testing_dashboard')
    
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        tester_id = request.POST.get('tester_id')
        tester = get_object_or_404(User, id=tester_id)
        
        issue.tester = tester
        issue.testing_status = 'in_testing'
        issue.save()
        
        # Create notification
        Notification.objects.create(
            recipient=tester,
            sender=user,
            notification_type='testing_assigned',
            issue=issue,
            message=f'{user.username} assigned you to test: {issue.title}'
        )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=user,
            action='assigned',
            field_changed='tester',
            new_value=tester.username
        )
        
        messages.success(request, f'Tester {tester.username} assigned successfully.')
        return redirect('testing_dashboard')
    
    return redirect('testing_dashboard')


@login_required
def complete_testing(request, issue_id):
    """Mark testing as completed"""
    issue = get_object_or_404(Issue, id=issue_id)
    
    # Check if user is the assigned tester
    if issue.tester != request.user:
        messages.error(request, 'You are not assigned to test this issue.')
        return redirect('testing_dashboard')
    
    if request.method == 'POST':
        testing_status = request.POST.get('testing_status')  # 'passed' or 'failed'
        testing_notes = request.POST.get('testing_notes', '')
        
        issue.testing_status = testing_status
        issue.testing_completed_at = timezone.now()
        issue.testing_notes = testing_notes
        
        if testing_status == 'passed':
            issue.status = 'done'
            notification_type = 'testing_passed'
            message = f'Testing passed for: {issue.title}. Issue marked as DONE!'
        else:
            issue.status = 'in_progress'
            notification_type = 'testing_failed'
            message = f'Testing failed for: {issue.title}. Please fix the issues.'
        
        issue.save()
        
        # Notify admin and scrum masters
        admins_and_scrum = User.objects.filter(Q(is_staff=True) | Q(groups__name='Scrum Master')).distinct()
        
        for admin in admins_and_scrum:
            if admin != request.user:
                Notification.objects.create(
                    recipient=admin,
                    sender=request.user,
                    notification_type=notification_type,
                    issue=issue,
                    message=message
                )
        
        # Notify issue owner
        if issue.assignee and issue.assignee != request.user:
            Notification.objects.create(
                recipient=issue.assignee,
                sender=request.user,
                notification_type=notification_type,
                issue=issue,
                message=message
            )
        
        # Log activity
        ActivityLog.objects.create(
            issue=issue,
            user=request.user,
            action='status_changed',
            field_changed='testing_status',
            new_value=testing_status
        )
        
        messages.success(request, f'Testing marked as {testing_status}.')
        return redirect('testing_dashboard')
    
    return redirect('testing_dashboard')


@login_required
def assign_sprint_tester(request, sprint_id):
    """Assign a tester to a sprint"""
    user = request.user
    
    # Check permissions
    if not (user.is_staff or user.groups.filter(name='Scrum Master').exists()):
        messages.error(request, 'You do not have permission to assign testers.')
        return redirect('testing_dashboard')
    
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    if request.method == 'POST':
        tester_id = request.POST.get('tester_id')
        tester = get_object_or_404(User, id=tester_id)
        
        sprint.tester = tester
        sprint.testing_status = 'in_testing'
        sprint.save()
        
        # Create notification
        Notification.objects.create(
            recipient=tester,
            sender=user,
            notification_type='testing_assigned',
            sprint=sprint,
            message=f'{user.username} assigned you to test sprint: {sprint.name}'
        )
        
        messages.success(request, f'Tester {tester.username} assigned to sprint successfully.')
        return redirect('testing_dashboard')
    
    return redirect('testing_dashboard')


@login_required
def complete_sprint_testing(request, sprint_id):
    """Mark sprint testing as completed"""
    sprint = get_object_or_404(Sprint, id=sprint_id)
    
    # Check if user is the assigned tester
    if sprint.tester != request.user:
        messages.error(request, 'You are not assigned to test this sprint.')
        return redirect('testing_dashboard')
    
    if request.method == 'POST':
        testing_status = request.POST.get('testing_status')  # 'passed' or 'failed'
        testing_notes = request.POST.get('testing_notes', '')
        
        sprint.testing_status = testing_status
        sprint.testing_completed_at = timezone.now()
        sprint.testing_notes = testing_notes
        
        if testing_status == 'passed':
            sprint.status = 'done'
            notification_type = 'testing_passed'
            message = f'Testing passed for sprint: {sprint.name}. Sprint marked as DONE!'
        else:
            sprint.status = 'active'
            notification_type = 'testing_failed'
            message = f'Testing failed for sprint: {sprint.name}. Please fix the issues.'
        
        sprint.save()
        
        # Notify admin and scrum masters
        admins_and_scrum = User.objects.filter(Q(is_staff=True) | Q(groups__name='Scrum Master')).distinct()
        
        for admin in admins_and_scrum:
            if admin != request.user:
                Notification.objects.create(
                    recipient=admin,
                    sender=request.user,
                    notification_type=notification_type,
                    sprint=sprint,
                    message=message
                )
        
        # Notify sprint team lead
        if sprint.team_lead and sprint.team_lead != request.user:
            Notification.objects.create(
                recipient=sprint.team_lead,
                sender=request.user,
                notification_type=notification_type,
                sprint=sprint,
                message=message
            )
        
        messages.success(request, f'Sprint testing marked as {testing_status}.')
        return redirect('testing_dashboard')
    
    return redirect('testing_dashboard')


# ===================== NOTIFICATION VIEWS =====================

@login_required
def notifications_view(request):
    """View all notifications for the user"""
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'issue')
    
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'sprint/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect('notifications_view')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications_view')


@login_required
def get_unread_notifications_count(request):
    """API endpoint to get unread notifications count"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def get_notifications_json(request):
    """API endpoint to get recent notifications"""
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'issue')[:10]
    
    data = [{
        'id': n.id,
        'type': n.notification_type,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'sender': n.sender.username if n.sender else 'System',
        'issue_id': n.issue.id if n.issue else None,
    } for n in notifications]
    
    return JsonResponse({'notifications': data})

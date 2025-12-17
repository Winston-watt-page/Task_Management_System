from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q, Count
from Projects.models import Project
from Sprint.models import Sprint, Issue
from Group.models import GroupPermissionProfile

# Helper function to check if user is admin
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

# Helper function to check if user is scrum master
def is_scrum_master(user):
    return user.groups.filter(name='Scrum Master').exists()

# Helper function to check if user is TL
def is_tl(user):
    return user.groups.filter(name='TL').exists()

# Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Assign to Admin group if first user
        if User.objects.count() == 1:
            admin_group, created = Group.objects.get_or_create(name='Admin')
            user.groups.add(admin_group)
            user.is_staff = True
            user.save()
            messages.success(request, 'Admin account created successfully!')
        else:
            messages.success(request, 'Account created successfully! Please wait for admin to assign you a role.')
        
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'accounts/register.html')

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'accounts/login.html')

# Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')

# Dashboard View
@login_required
def dashboard_view(request):
    user = request.user
    user_groups = user.groups.all()
    
    # Get statistics based on role
    context = {
        'user': user,
        'groups': user_groups,
    }
    
    if is_admin(user):
        context.update({
            'total_projects': Project.objects.count(),
            'total_users': User.objects.count(),
            'active_sprints': Sprint.objects.filter(status='active').count(),
            'total_issues': Issue.objects.count(),
            'recent_projects': Project.objects.all()[:5],
        })
        return render(request, 'accounts/dashboard_admin.html', context)
    
    elif is_tl(user):
        context.update({
            'my_sprints': Sprint.objects.filter(team_lead=user),
            'active_sprints': Sprint.objects.filter(team_lead=user, status='active'),
        })
        return render(request, 'accounts/dashboard_tl.html', context)
    
    elif is_scrum_master(user):
        context.update({
            'total_sprints': Sprint.objects.count(),
            'active_sprints': Sprint.objects.filter(status='active'),
            'total_issues': Issue.objects.count(),
        })
        return render(request, 'accounts/dashboard_scrum_master.html', context)
    
    else:  # Developer or Tester
        context.update({
            'my_issues': Issue.objects.filter(assignee=user),
            'todo_issues': Issue.objects.filter(assignee=user, status='todo'),
            'in_progress_issues': Issue.objects.filter(assignee=user, status='in_progress'),
            'completed_issues': Issue.objects.filter(assignee=user, status='completed'),
            'my_sprints': Sprint.objects.filter(assignee=user),
        })
        return render(request, 'accounts/dashboard_user.html', context)

# User Management (Admin Only)
@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = User.objects.all().prefetch_related('groups')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        group_id = request.POST.get('group')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('user_create')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Assign group
        if group_id:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)
        
        messages.success(request, f'User {username} created successfully!')
        return redirect('user_list')
    
    groups = Group.objects.all()
    return render(request, 'accounts/user_create.html', {'groups': groups})

@login_required
@user_passes_test(is_admin)
def user_edit_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.email = request.POST.get('email')
        group_id = request.POST.get('group')
        
        user_obj.save()
        
        # Update group
        if group_id:
            user_obj.groups.clear()
            group = Group.objects.get(id=group_id)
            user_obj.groups.add(group)
        
        messages.success(request, f'User {user_obj.username} updated successfully!')
        return redirect('user_list')
    
    groups = Group.objects.all()
    user_group = user_obj.groups.first()
    return render(request, 'accounts/user_edit.html', {
        'user_obj': user_obj,
        'groups': groups,
        'user_group': user_group
    })

@login_required
@user_passes_test(is_admin)
def user_delete_view(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.user == user_obj:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('user_list')
    
    username = user_obj.username
    user_obj.delete()
    messages.success(request, f'User {username} deleted successfully!')
    return redirect('user_list')

# Group Management (Admin Only)
@login_required
@user_passes_test(is_admin)
def group_list_view(request):
    groups = Group.objects.all().annotate(user_count=Count('user'))
    return render(request, 'accounts/group_list.html', {'groups': groups})

@login_required
@user_passes_test(is_admin)
def group_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Create group
        group, created = Group.objects.get_or_create(name=name)
        
        if created:
            # Create permission profile
            GroupPermissionProfile.objects.create(
                group=group,
                description=description,
                can_create_projects=request.POST.get('can_create_projects') == 'on',
                can_manage_users=request.POST.get('can_manage_users') == 'on',
                can_create_sprints=request.POST.get('can_create_sprints') == 'on',
                can_start_sprints=request.POST.get('can_start_sprints') == 'on',
                can_assign_tasks=request.POST.get('can_assign_tasks') == 'on',
                can_update_any_task=request.POST.get('can_update_any_task') == 'on',
            )
            messages.success(request, f'Group {name} created successfully!')
        else:
            messages.warning(request, f'Group {name} already exists!')
        
        return redirect('group_list')
    
    return render(request, 'accounts/group_create.html')

# Admin Backlog View
@login_required
@user_passes_test(is_admin)
def admin_backlog_view(request):
    projects = Project.objects.all()
    issues = Issue.objects.filter(sprint__isnull=True).select_related('project', 'assignee')
    
    return render(request, 'accounts/backlog.html', {
        'projects': projects,
        'issues': issues
    })

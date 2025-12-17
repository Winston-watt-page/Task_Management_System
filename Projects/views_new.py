from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Epic, Label
from Sprint.models import Issue

@login_required
def project_list_view(request):
    projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    epics = project.epics.all()
    sprints = project.sprints.all()
    issues = project.issues.all()
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'epics': epics,
        'sprints': sprints,
        'issues': issues
    })

@login_required
def project_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        key = request.POST.get('key').upper()
        description = request.POST.get('description')
        
        if Project.objects.filter(key=key).exists():
            messages.error(request, f'Project with key {key} already exists!')
            return redirect('project_create')
        
        project = Project.objects.create(
            name=name,
            key=key,
            description=description,
            created_by=request.user
        )
        
        messages.success(request, f'Project {name} created successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/project_create.html')

@login_required
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description')
        project.status = request.POST.get('status')
        project.save()
        
        messages.success(request, f'Project {project.name} updated successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/project_edit.html', {'project': project})

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission class for Admin users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsTeamLeader(permissions.BasePermission):
    """Permission class for Team Leader users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'TEAM_LEADER']


class IsEmployee(permissions.BasePermission):
    """Permission class for Employee users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_employee or request.user.role == 'ADMIN')


class IsReviewer(permissions.BasePermission):
    """Permission class for Reviewer users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'TEAM_LEADER', 'REVIEWER']


class IsOwnerOrTeamLeader(permissions.BasePermission):
    """Permission class for object owners or team leaders"""
    
    def has_object_permission(self, request, view, obj):
        # Allow GET for everyone authenticated
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin and Team Leaders can modify
        if request.user.role in ['ADMIN', 'TEAM_LEADER']:
            return True
        
        # Object owner can modify
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanManageProject(permissions.BasePermission):
    """Permission for project management"""
    
    def has_permission(self, request, view):
        # List/Read: All authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Create/Update/Delete: Admin or Team Leader
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'TEAM_LEADER']
    
    def has_object_permission(self, request, view, obj):
        # Read: All authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Update/Delete: Admin, project creator, or team leader
        if request.user.role in ['ADMIN', 'TEAM_LEADER']:
            return True
        
        return obj.created_by == request.user


class CanManageTask(permissions.BasePermission):
    """Permission for task management"""
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if view and view.action == 'change_status':
            return True
        
        if request.method in ['POST', 'DELETE']:
            return user.role in ['ADMIN', 'TEAM_LEADER']
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Read: Everyone who has access to the project
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Delete: Admin or Team Leader only
        if request.method == 'DELETE' or (view and view.action == 'destroy'):
            return request.user.role in ['ADMIN', 'TEAM_LEADER']
        
        # Custom change_status action: allow assigned employee
        if view and view.action == 'change_status':
            if request.user.role in ['ADMIN', 'TEAM_LEADER']:
                return True
            return obj.assigned_to == request.user
        
        # Update: Admin, Team Leader, or assigned employee
        if request.method in ['PUT', 'PATCH'] or (view and view.action in ['update', 'partial_update']):
            if request.user.role in ['ADMIN', 'TEAM_LEADER']:
                return True
            return obj.assigned_to == request.user
        
        return False


class CanManageReview(permissions.BasePermission):
    """Permission for review management"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read: Admin, TL, submitter, or assigned reviewer
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user.role in ['ADMIN', 'TEAM_LEADER'] or
                obj.submitted_by == request.user or
                obj.reviewer == request.user
            )
        
        # Create: Employee submitting review (handled via view action)
        if view and view.action == 'create':
            return True
        
        # Custom actions: assign_reviewer (TL/Admin), approve/request_changes (Reviewer/TL/Admin)
        if view and view.action == 'assign_reviewer':
            return request.user.role in ['ADMIN', 'TEAM_LEADER']
        
        if view and view.action in ['approve', 'request_changes']:
            return (
                request.user.role in ['ADMIN', 'TEAM_LEADER'] or
                obj.reviewer == request.user
            )
        
        # Update: Admin, TL, or assigned reviewer
        if request.method in ['PUT', 'PATCH'] or (view and view.action in ['update', 'partial_update']):
            return (
                request.user.role in ['ADMIN', 'TEAM_LEADER'] or
                obj.reviewer == request.user
            )
        
        if request.method == 'POST':
            return (
                request.user.role in ['ADMIN', 'TEAM_LEADER'] or
                obj.reviewer == request.user
            )

        return False

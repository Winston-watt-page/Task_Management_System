"""
Test cases for custom permissions
"""
from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from tasks.models import User, Team, Project, Task
from tasks.permissions import (
    IsAdmin, IsTeamLeader, IsEmployee, IsReviewer,
    CanManageProject, CanManageTask, CanManageReview
)


class PermissionTestCase(TestCase):
    """Base test case for permissions"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='ADMIN'
        )
        
        self.team_leader = User.objects.create_user(
            username='teamlead',
            password='tl123',
            role='TEAM_LEADER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='emp123',
            role='EMPLOYEE'
        )
        
        self.reviewer = User.objects.create_user(
            username='reviewer',
            password='reviewer123',
            role='REVIEWER'
        )
        
        # Create team and project
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            created_by=self.team_leader
        )
        
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader
        )


class RoleBasedPermissionTest(PermissionTestCase):
    """Test role-based permissions"""
    
    def test_is_admin_permission(self):
        """Test IsAdmin permission"""
        permission = IsAdmin()
        request = self.factory.get('/')
        
        # Admin should have permission
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Non-admin should not have permission
        request.user = self.employee
        self.assertFalse(permission.has_permission(request, None))
    
    def test_is_team_leader_permission(self):
        """Test IsTeamLeader permission"""
        permission = IsTeamLeader()
        request = self.factory.get('/')
        
        # Team leader should have permission
        request.user = self.team_leader
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin should also have permission
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Employee should not have permission
        request.user = self.employee
        self.assertFalse(permission.has_permission(request, None))
    
    def test_is_employee_permission(self):
        """Test IsEmployee permission"""
        permission = IsEmployee()
        request = self.factory.get('/')
        
        # Employee should have permission
        request.user = self.employee
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin should also have permission
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Reviewer should not have permission
        request.user = self.reviewer
        self.assertFalse(permission.has_permission(request, None))
    
    def test_is_reviewer_permission(self):
        """Test IsReviewer permission"""
        permission = IsReviewer()
        request = self.factory.get('/')
        
        # Reviewer should have permission
        request.user = self.reviewer
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin should also have permission
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Employee should not have permission
        request.user = self.employee
        self.assertFalse(permission.has_permission(request, None))


class ProjectPermissionTest(PermissionTestCase):
    """Test project-related permissions"""
    
    def test_can_manage_project_create(self):
        """Test project creation permissions"""
        permission = CanManageProject()
        request = self.factory.post('/')
        
        # Team leader can create
        request.user = self.team_leader
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin can create
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Employee cannot create
        request.user = self.employee
        self.assertFalse(permission.has_permission(request, None))
    
    def test_can_manage_project_read(self):
        """Test project read permissions"""
        permission = CanManageProject()
        request = self.factory.get('/')
        
        # All authenticated users can read
        for user in [self.admin, self.team_leader, self.employee, self.reviewer]:
            request.user = user
            self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_project_update(self):
        """Test project update permissions"""
        permission = CanManageProject()
        request = self.factory.put('/')
        
        # Team leader of the project can update
        request.user = self.team_leader
        self.assertTrue(permission.has_object_permission(request, None, self.project))
        
        # Admin can update
        request.user = self.admin
        self.assertTrue(permission.has_object_permission(request, None, self.project))
        
        # Employee cannot update
        request.user = self.employee
        self.assertFalse(permission.has_object_permission(request, None, self.project))


class TaskPermissionTest(PermissionTestCase):
    """Test task-related permissions"""
    
    def test_can_manage_task_create(self):
        """Test task creation permissions"""
        permission = CanManageTask()
        request = self.factory.post('/')
        
        # Team leader can create tasks
        request.user = self.team_leader
        self.assertTrue(permission.has_permission(request, None))
        
        # Admin can create tasks
        request.user = self.admin
        self.assertTrue(permission.has_permission(request, None))
        
        # Employee cannot create tasks
        request.user = self.employee
        self.assertFalse(permission.has_permission(request, None))
    
    def test_can_manage_task_read(self):
        """Test task read permissions"""
        permission = CanManageTask()
        request = self.factory.get('/')
        
        # All authenticated users can read
        for user in [self.admin, self.team_leader, self.employee]:
            request.user = user
            self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_task_update(self):
        """Test task update permissions"""
        permission = CanManageTask()
        request = self.factory.put('/')
        
        # Assigned employee can update
        request.user = self.employee
        self.assertTrue(permission.has_object_permission(request, None, self.task))
        
        # Team leader can update
        request.user = self.team_leader
        self.assertTrue(permission.has_object_permission(request, None, self.task))
        
        # Admin can update
        request.user = self.admin
        self.assertTrue(permission.has_object_permission(request, None, self.task))
        
        # Different employee cannot update
        other_employee = User.objects.create_user(
            username='other_emp',
            password='pass',
            role='EMPLOYEE'
        )
        request.user = other_employee
        self.assertFalse(permission.has_object_permission(request, None, self.task))
    
    def test_can_manage_task_delete(self):
        """Test task deletion permissions"""
        permission = CanManageTask()
        request = self.factory.delete('/')
        
        # Admin can delete
        request.user = self.admin
        self.assertTrue(permission.has_object_permission(request, None, self.task))
        
        # Team leader can delete
        request.user = self.team_leader
        self.assertTrue(permission.has_object_permission(request, None, self.task))
        
        # Employee cannot delete
        request.user = self.employee
        self.assertFalse(permission.has_object_permission(request, None, self.task))


class ReviewPermissionTest(PermissionTestCase):
    """Test review-related permissions"""
    
    def test_can_manage_review_create(self):
        """Test review creation permissions"""
        from tasks.permissions import CanManageReview
        permission = CanManageReview()
        request = self.factory.post('/')
        
        # Employee who owns the task can create review
        request.user = self.employee
        request.data = {'task': self.task.id}
        # In real scenario, this would be checked in the view
        # Here we just test the basic permission logic
        self.assertTrue(permission.has_permission(request, None))
    
    def test_can_manage_review_approve(self):
        """Test review approval permissions"""
        from tasks.models import Review
        from tasks.permissions import CanManageReview
        
        review = Review.objects.create(
            task=self.task,
            submitted_by=self.employee,
            reviewer=self.reviewer,
            status='IN_REVIEW'
        )
        
        permission = CanManageReview()
        request = self.factory.post('/')
        
        # Assigned reviewer can approve
        request.user = self.reviewer
        self.assertTrue(permission.has_object_permission(request, None, review))
        
        # Admin can approve
        request.user = self.admin
        self.assertTrue(permission.has_object_permission(request, None, review))
        
        # Other users cannot approve
        request.user = self.employee
        self.assertFalse(permission.has_object_permission(request, None, review))

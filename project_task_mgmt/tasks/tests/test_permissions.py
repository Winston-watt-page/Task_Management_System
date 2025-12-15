"""
Unit tests for permissions in the tasks app
"""
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from datetime import date
from tasks.models import Team, Project, Task, Sprint
from tasks.permissions import (
    IsAdmin, IsTeamLeader, IsEmployee, IsReviewer,
    CanManageProject, CanManageTask
)

User = get_user_model()


@pytest.mark.django_db
class TestIsAdminPermission(TestCase):
    """Test cases for IsAdmin permission"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = IsAdmin()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='ADMIN'
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
    
    def test_admin_has_permission(self):
        """Test admin user has permission"""
        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_employee_no_permission(self):
        """Test employee user has no permission"""
        request = self.factory.get('/')
        request.user = self.employee
        self.assertFalse(self.permission.has_permission(request, None))


@pytest.mark.django_db
class TestIsTeamLeaderPermission(TestCase):
    """Test cases for IsTeamLeader permission"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = IsTeamLeader()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='ADMIN'
        )
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
    
    def test_admin_has_permission(self):
        """Test admin has team leader permission"""
        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_team_leader_has_permission(self):
        """Test team leader has permission"""
        request = self.factory.get('/')
        request.user = self.team_leader
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_employee_no_permission(self):
        """Test employee has no permission"""
        request = self.factory.get('/')
        request.user = self.employee
        self.assertFalse(self.permission.has_permission(request, None))


@pytest.mark.django_db
class TestIsEmployeePermission(TestCase):
    """Test cases for IsEmployee permission"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = IsEmployee()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='ADMIN'
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
    
    def test_admin_has_permission(self):
        """Test admin has employee permission"""
        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_employee_has_permission(self):
        """Test employee has permission"""
        request = self.factory.get('/')
        request.user = self.employee
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_team_leader_has_permission(self):
        """Test team leader has employee permission"""
        request = self.factory.get('/')
        request.user = self.team_leader
        self.assertTrue(self.permission.has_permission(request, None))


@pytest.mark.django_db
class TestCanManageProjectPermission(TestCase):
    """Test cases for CanManageProject permission"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = CanManageProject()
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=date.today()
        )
    
    def test_read_permission_for_authenticated(self):
        """Test read permission for authenticated users"""
        request = self.factory.get('/')
        request.user = self.employee
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_create_permission_for_team_leader(self):
        """Test create permission for team leader"""
        request = self.factory.post('/')
        request.user = self.team_leader
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_create_permission_denied_for_employee(self):
        """Test create permission denied for employee"""
        request = self.factory.post('/')
        request.user = self.employee
        self.assertFalse(self.permission.has_permission(request, None))
    
    def test_object_permission_for_creator(self):
        """Test object permission for project creator"""
        request = self.factory.put('/')
        request.user = self.team_leader
        self.assertTrue(self.permission.has_object_permission(request, None, self.project))


@pytest.mark.django_db
class TestCanManageTaskPermission(TestCase):
    """Test cases for CanManageTask permission"""
    
    def setUp(self):
        """Set up test data"""
        self.factory = APIRequestFactory()
        self.permission = CanManageTask()
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=date.today()
        )
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            start_date=date.today(),
            end_date=date.today()
        )
        self.task = Task.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Task',
            assigned_to=self.employee,
            assigned_by=self.team_leader
        )
    
    def test_read_permission(self):
        """Test read permission for tasks"""
        request = self.factory.get('/')
        request.user = self.employee
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_create_permission_for_team_leader(self):
        """Test create permission for team leader"""
        request = self.factory.post('/')
        request.user = self.team_leader
        self.assertTrue(self.permission.has_permission(request, None))
    
    def test_create_permission_denied_for_employee(self):
        """Test create permission denied for employee"""
        request = self.factory.post('/')
        request.user = self.employee
        self.assertFalse(self.permission.has_permission(request, None))

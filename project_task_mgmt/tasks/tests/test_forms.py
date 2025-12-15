"""
Unit tests for forms in the tasks app
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from tasks.models import Team, Project, Sprint, Task
from tasks.forms import (
    UserRegistrationForm, UserLoginForm, ProjectForm,
    SprintForm, TaskForm, ReviewForm
)

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationForm(TestCase):
    """Test cases for UserRegistrationForm"""
    
    def test_valid_registration_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'EMPLOYEE'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'EMPLOYEE'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'wrongpass',
            'role': 'EMPLOYEE'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


@pytest.mark.django_db
class TestUserLoginForm(TestCase):
    """Test cases for UserLoginForm"""
    
    def test_valid_login_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_username(self):
        """Test form with empty username"""
        form_data = {
            'username': '',
            'password': 'testpass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_empty_password(self):
        """Test form with empty password"""
        form_data = {
            'username': 'testuser',
            'password': ''
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())


@pytest.mark.django_db
class TestProjectForm(TestCase):
    """Test cases for ProjectForm"""
    
    def setUp(self):
        """Set up test data"""
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
    
    def test_valid_project_form(self):
        """Test form with valid data"""
        form_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'team': self.team.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'status': 'PLANNING'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_name(self):
        """Test form with empty name"""
        form_data = {
            'name': '',
            'team': self.team.id,
            'start_date': date.today(),
            'status': 'PLANNING'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())


@pytest.mark.django_db
class TestSprintForm(TestCase):
    """Test cases for SprintForm"""
    
    def setUp(self):
        """Set up test data"""
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
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
    
    def test_valid_sprint_form(self):
        """Test form with valid data"""
        form_data = {
            'name': 'Sprint 1',
            'goal': 'Complete features',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=14),
            'status': 'PLANNING',
            'capacity': 100
        }
        form = SprintForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_date_range(self):
        """Test form with end date before start date"""
        form_data = {
            'project': self.project.id,
            'name': 'Sprint 1',
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=1),
            'status': 'PLANNING'
        }
        form = SprintForm(data=form_data)
        # Note: The form validation for date range should be added to the form
        # This is a placeholder test


@pytest.mark.django_db
class TestTaskForm(TestCase):
    """Test cases for TaskForm"""
    
    def setUp(self):
        """Set up test data"""
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
            end_date=date.today() + timedelta(days=14)
        )
    
    def test_valid_task_form(self):
        """Test form with valid data"""
        form_data = {
            'project': self.project.id,
            'sprint': self.sprint.id,
            'title': 'Test Task',
            'description': 'Task description',
            'assigned_to': self.employee.id,
            'priority': 'P1',
            'status': 'OPEN',
            'estimated_hours': 5
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_title(self):
        """Test form with empty title"""
        form_data = {
            'project': self.project.id,
            'title': '',
            'priority': 'P1',
            'status': 'OPEN'
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())

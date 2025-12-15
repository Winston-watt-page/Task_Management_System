"""
Unit tests for serializers in the tasks app
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from tasks.models import Team, Project, Sprint, Task, Review
from tasks.serializers import (
    UserSerializer, UserListSerializer, LoginSerializer,
    TeamSerializer, ProjectSerializer, SprintSerializer,
    TaskSerializer, ReviewSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer(TestCase):
    """Test cases for UserSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'role': 'EMPLOYEE'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@test.com',
            password='testpass123',
            role='ADMIN'
        )
    
    def test_user_serializer_create(self):
        """Test user creation through serializer"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_serializer_update(self):
        """Test user update through serializer"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        serializer = UserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
    
    def test_user_serializer_password_write_only(self):
        """Test password is write-only"""
        serializer = UserSerializer(self.user)
        self.assertNotIn('password', serializer.data)
    
    def test_user_list_serializer(self):
        """Test UserListSerializer"""
        serializer = UserListSerializer(self.user)
        self.assertIn('username', serializer.data)
        self.assertIn('email', serializer.data)
        self.assertNotIn('password', serializer.data)


@pytest.mark.django_db
class TestLoginSerializer(TestCase):
    """Test cases for LoginSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@test.com',
            password='testpass123',
            is_active=False
        )
    
    def test_login_serializer_valid(self):
        """Test valid login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    def test_login_serializer_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_login_serializer_inactive_user(self):
        """Test login with inactive user"""
        data = {
            'username': 'inactive',
            'password': 'testpass123'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())


@pytest.mark.django_db
class TestTeamSerializer(TestCase):
    """Test cases for TeamSerializer"""
    
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
            description='Development team',
            team_leader=self.team_leader
        )
    
    def test_team_serializer_read(self):
        """Test reading team data"""
        serializer = TeamSerializer(self.team)
        self.assertEqual(serializer.data['name'], 'Dev Team')
        self.assertEqual(serializer.data['team_leader'], self.team_leader.id)
        self.assertIn('team_leader_detail', serializer.data)
    
    def test_team_serializer_create(self):
        """Test team creation through serializer"""
        data = {
            'name': 'New Team',
            'description': 'A new team',
            'team_leader': self.team_leader.id,
            'members': []
        }
        serializer = TeamSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        team = serializer.save()
        self.assertEqual(team.name, 'New Team')


@pytest.mark.django_db
class TestProjectSerializer(TestCase):
    """Test cases for ProjectSerializer"""
    
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
    
    def test_project_serializer_read(self):
        """Test reading project data"""
        serializer = ProjectSerializer(self.project)
        self.assertEqual(serializer.data['name'], 'Test Project')
        self.assertIn('team', serializer.data)
    
    def test_project_serializer_create(self):
        """Test project creation through serializer"""
        data = {
            'name': 'New Project',
            'description': 'A new project',
            'team': self.team.id,
            'start_date': str(date.today()),
            'status': 'PLANNING'
        }
        serializer = ProjectSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        project = serializer.save(created_by=self.team_leader)
        self.assertEqual(project.name, 'New Project')


@pytest.mark.django_db
class TestSprintSerializer(TestCase):
    """Test cases for SprintSerializer"""
    
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
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
    
    def test_sprint_serializer_read(self):
        """Test reading sprint data"""
        serializer = SprintSerializer(self.sprint)
        self.assertEqual(serializer.data['name'], 'Sprint 1')
        self.assertEqual(serializer.data['project'], self.project.id)
    
    def test_sprint_serializer_create(self):
        """Test sprint creation through serializer"""
        data = {
            'project': self.project.id,
            'name': 'Sprint 2',
            'goal': 'Complete features',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=14)),
            'status': 'PLANNING'
        }
        serializer = SprintSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        sprint = serializer.save()
        self.assertEqual(sprint.name, 'Sprint 2')


@pytest.mark.django_db
class TestTaskSerializer(TestCase):
    """Test cases for TaskSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.employee = User.objects.create_user(
            username='emp',
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
        self.task = Task.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Task',
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='OPEN'
        )
    
    def test_task_serializer_read(self):
        """Test reading task data"""
        serializer = TaskSerializer(self.task)
        self.assertEqual(serializer.data['title'], 'Test Task')
        self.assertEqual(serializer.data['status'], 'OPEN')
    
    def test_task_serializer_create(self):
        """Test task creation through serializer"""
        data = {
            'project': self.project.id,
            'sprint': self.sprint.id,
            'title': 'New Task',
            'description': 'Task description',
            'assigned_to': self.employee.id,
            'priority': 'P1',
            'status': 'OPEN',
            'estimated_hours': 5
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save(assigned_by=self.team_leader)
        self.assertEqual(task.title, 'New Task')

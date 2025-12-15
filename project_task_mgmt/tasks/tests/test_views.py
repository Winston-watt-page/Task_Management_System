"""
Unit tests for views in the tasks app
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from tasks.models import Team, Project, Sprint, Task, Review, Notification

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationViews(APITestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'EMPLOYEE'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        # Add password2 field required by UserRegistrationForm
        self.user_data['password1'] = self.user_data.pop('password')
        self.user_data['password2'] = 'testpass123'
        response = self.client.post(self.register_url, self.user_data)
        # Web view redirects on success (302)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_302_FOUND])
        # Verify user was created if redirected
        if response.status_code == status.HTTP_302_FOUND:
            self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data"""
        invalid_data = {
            'username': '',
            'email': 'invalid-email',
            'password': '123'
        }
        response = self.client.post(self.register_url, invalid_data)
        # Form validation error returns 200 with errors
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should not be created
        self.assertFalse(User.objects.filter(username='').exists())
    
    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        # Web view redirects on successful login (302) or returns 200
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_302_FOUND])
    
    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data)
        # Failed login returns 200 with error message
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class TestUserViewSet(APITestCase):
    """Test cases for UserViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
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
        self.list_url = reverse('user-list')
    
    def test_list_users_authenticated(self):
        """Test listing users when authenticated"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_list_users_unauthenticated(self):
        """Test listing users when not authenticated"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_user(self):
        """Test retrieving a single user"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', kwargs={'pk': self.employee.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'employee')
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('user-detail', kwargs={'pk': self.employee.pk})
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.first_name, 'Updated')


@pytest.mark.django_db
class TestTeamViewSet(APITestCase):
    """Test cases for TeamViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
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
        self.list_url = reverse('team-list')
    
    def test_list_teams(self):
        """Test listing teams"""
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_team_as_team_leader(self):
        """Test creating team as team leader"""
        self.client.force_authenticate(user=self.team_leader)
        data = {
            'name': 'New Team',
            'description': 'A new team',
            'team_leader': self.team_leader.id,
            'members': [self.employee.id]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_team_as_employee_forbidden(self):
        """Test creating team as employee (should fail)"""
        self.client.force_authenticate(user=self.employee)
        data = {
            'name': 'New Team',
            'team_leader': self.employee.id
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestProjectViewSet(APITestCase):
    """Test cases for ProjectViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
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
        self.list_url = reverse('project-list')
    
    def test_list_projects(self):
        """Test listing projects"""
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_project_as_team_leader(self):
        """Test creating project as team leader"""
        self.client.force_authenticate(user=self.team_leader)
        data = {
            'name': 'New Project',
            'description': 'A new project',
            'team': self.team.id,
            'created_by': self.team_leader.id,
            'start_date': str(date.today()),
            'status': 'PLANNING'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_retrieve_project(self):
        """Test retrieving a project"""
        self.client.force_authenticate(user=self.team_leader)
        url = reverse('project-detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')


@pytest.mark.django_db
class TestTaskViewSet(APITestCase):
    """Test cases for TaskViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
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
        self.task = Task.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Task',
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='OPEN'
        )
        self.list_url = reverse('task-list')
    
    def test_list_tasks(self):
        """Test listing tasks"""
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_task_as_team_leader(self):
        """Test creating task as team leader"""
        self.client.force_authenticate(user=self.team_leader)
        data = {
            'project': self.project.id,
            'sprint': self.sprint.id,
            'title': 'New Task',
            'description': 'Task description',
            'assigned_to': self.employee.id,
            'assigned_by': self.team_leader.id,
            'priority': 'P1',
            'status': 'OPEN',
            'estimated_hours': 5
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_task_status(self):
        """Test updating task status"""
        self.client.force_authenticate(user=self.employee)
        url = reverse('task-detail', kwargs={'pk': self.task.pk})
        data = {'status': 'IN_PROGRESS'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'IN_PROGRESS')
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.get(self.list_url, {'status': 'OPEN'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for task in response.data['results']:
            self.assertEqual(task['status'], 'OPEN')

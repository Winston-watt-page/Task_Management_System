"""
Test cases for web views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tasks.models import User, Team, Project, Sprint, Task, Review, Notification


class WebViewTestCase(TestCase):
    """Base test case for web views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='ADMIN'
        )
        
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='tl@test.com',
            password='tl123',
            role='TEAM_LEADER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='emp@test.com',
            password='emp123',
            role='EMPLOYEE'
        )
        
        # Create team and project
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        self.team.members.add(self.team_leader, self.employee)
        
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            created_by=self.team_leader
        )


class AuthenticationViewTest(WebViewTestCase):
    """Test authentication views"""
    
    def test_login_page_get(self):
        """Test login page renders"""
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/auth/login.html')
    
    def test_login_post_success(self):
        """Test successful login"""
        url = reverse('login')
        data = {
            'username': 'employee',
            'password': 'emp123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_login_post_failure(self):
        """Test failed login with wrong credentials"""
        url = reverse('login')
        data = {
            'username': 'employee',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='employee', password='emp123')
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
    
    def test_register_page_get(self):
        """Test registration page renders"""
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/auth/register.html')
    
    def test_register_post_success(self):
        """Test successful user registration"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'role': 'EMPLOYEE',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class DashboardViewTest(WebViewTestCase):
    """Test dashboard view"""
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_renders_for_logged_in_user(self):
        """Test dashboard renders for authenticated user"""
        self.client.login(username='employee', password='emp123')
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/dashboard.html')
    
    def test_dashboard_shows_statistics(self):
        """Test dashboard shows task statistics"""
        # Create some tasks
        Task.objects.create(
            title='Task 1',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='IN_PROGRESS'
        )
        Task.objects.create(
            title='Task 2',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='DONE'
        )
        
        self.client.login(username='employee', password='emp123')
        url = reverse('dashboard')
        response = self.client.get(url)
        
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')


class ProjectViewTest(WebViewTestCase):
    """Test project views"""
    
    def test_project_list_requires_login(self):
        """Test project list requires authentication"""
        url = reverse('project_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_project_list_renders(self):
        """Test project list renders"""
        self.client.login(username='teamlead', password='tl123')
        url = reverse('project_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_project_detail_renders(self):
        """Test project detail view"""
        self.client.login(username='teamlead', password='tl123')
        url = reverse('project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_project_create_get(self):
        """Test project create page renders"""
        self.client.login(username='teamlead', password='tl123')
        url = reverse('project_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_project_create_post(self):
        """Test creating a project"""
        self.client.login(username='teamlead', password='tl123')
        url = reverse('project_create')
        data = {
            'name': 'New Project',
            'description': 'New project description',
            'team': self.team.id,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=60),
            'status': 'PLANNING'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project').exists())


class TaskViewTest(WebViewTestCase):
    """Test task views"""
    
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            title='Test Task',
            description='Task description',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            priority='P1'
        )
    
    def test_task_list_requires_login(self):
        """Test task list requires authentication"""
        url = reverse('task_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_task_list_renders(self):
        """Test task list renders"""
        self.client.login(username='employee', password='emp123')
        url = reverse('task_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_detail_renders(self):
        """Test task detail view"""
        self.client.login(username='employee', password='emp123')
        url = reverse('task_detail', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
    
    def test_task_create_by_team_leader(self):
        """Test team leader can create task"""
        self.client.login(username='teamlead', password='tl123')
        url = reverse('task_create')
        data = {
            'title': 'New Task',
            'description': 'New task description',
            'project': self.project.id,
            'assigned_to': self.employee.id,
            'priority': 'P0',
            'estimated_hours': 8,
            'status': 'OPEN'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())
    
    def test_task_update_by_assigned_user(self):
        """Test assigned user can update task"""
        self.client.login(username='employee', password='emp123')
        url = reverse('task_update', kwargs={'pk': self.task.pk})
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'project': self.project.id,
            'assigned_to': self.employee.id,
            'priority': 'P2',
            'estimated_hours': 5,
            'status': 'IN_PROGRESS'
        }
        response = self.client.post(url, data)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'IN_PROGRESS')


class NotificationViewTest(WebViewTestCase):
    """Test notification views"""
    
    def setUp(self):
        super().setUp()
        self.notification = Notification.objects.create(
            user=self.employee,
            type='TASK_ASSIGNED',
            title='New Task',
            message='You have been assigned a new task'
        )
    
    def test_notification_list_requires_login(self):
        """Test notification list requires authentication"""
        url = reverse('notification_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_notification_list_renders(self):
        """Test notification list renders"""
        self.client.login(username='employee', password='emp123')
        url = reverse('notification_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Task')
    
    def test_mark_notification_as_read(self):
        """Test marking notification as read"""
        self.client.login(username='employee', password='emp123')
        url = reverse('notification_mark_read', kwargs={'pk': self.notification.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

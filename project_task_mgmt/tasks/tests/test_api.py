"""
Test cases for REST API endpoints
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from tasks.models import User, Team, Project, Sprint, Task, Review


class APITestCase(TestCase):
    """Base test case with common setup for API tests"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create users with different roles
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
        
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='reviewer123',
            role='REVIEWER'
        )
        
        # Create team and project
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        # Add team_leader and employee to team members
        self.team.members.add(self.team_leader, self.employee)
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            team=self.team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            created_by=self.team_leader
        )
    
    def get_token(self, user):
        """Get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate(self, user):
        """Authenticate client with user token"""
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def test_user_registration(self):
        """Test user registration"""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'role': 'EMPLOYEE',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
    
    def test_obtain_token(self):
        """Test JWT token generation"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Get initial token
        refresh = RefreshToken.for_user(self.admin)
        
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_unauthorized_access(self):
        """Test that unauthorized requests are rejected"""
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAPITest(APITestCase):
    """Test user endpoints"""
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        self.authenticate(self.employee)
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'employee')
    
    def test_list_users_as_admin(self):
        """Test admin can list all users"""
        self.authenticate(self.admin)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 4)
    
    def test_list_team_leaders(self):
        """Test listing team leaders"""
        self.authenticate(self.admin)
        url = reverse('user-team-leaders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'teamlead')


class ProjectAPITest(APITestCase):
    """Test project endpoints"""
    
    def test_list_projects(self):
        """Test listing projects"""
        self.authenticate(self.team_leader)
        url = reverse('project-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_project_as_team_leader(self):
        """Test team leader can create project"""
        self.authenticate(self.team_leader)
        url = reverse('project-list')
        data = {
            'name': 'New Project',
            'description': 'New Description',
            'team': self.team.id,
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=60)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.filter(name='New Project').count(), 1)
    
    def test_create_project_as_employee_fails(self):
        """Test employee cannot create project"""
        self.authenticate(self.employee)
        url = reverse('project-list')
        data = {
            'name': 'Unauthorized Project',
            'description': 'Should fail',
            'team': self.team.id,
            'start_date': timezone.now().date().isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=60)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_project_summary(self):
        """Test getting project summary statistics"""
        self.authenticate(self.team_leader)
        url = reverse('project-summary', kwargs={'pk': self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tasks', response.data)
        self.assertIn('completed_tasks', response.data)
        self.assertIn('progress_percentage', response.data)


class SprintAPITest(APITestCase):
    """Test sprint endpoints"""
    
    def setUp(self):
        super().setUp()
        self.sprint = Sprint.objects.create(
            name='Sprint 1',
            project=self.project,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=14),
            goal='Complete features'
        )
    
    def test_list_sprints(self):
        """Test listing sprints"""
        self.authenticate(self.employee)
        url = reverse('sprint-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_sprint_as_team_leader(self):
        """Test team leader can create sprint"""
        self.authenticate(self.team_leader)
        url = reverse('sprint-list')
        data = {
            'name': 'Sprint 2',
            'project': self.project.id,
            'start_date': (timezone.now().date() + timedelta(days=14)).isoformat(),
            'end_date': (timezone.now().date() + timedelta(days=28)).isoformat(),
            'goal': 'New features'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_start_sprint(self):
        """Test starting a sprint"""
        self.authenticate(self.team_leader)
        url = reverse('sprint-start', kwargs={'pk': self.sprint.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'ACTIVE')
    
    def test_complete_sprint(self):
        """Test completing a sprint"""
        self.sprint.status = 'ACTIVE'
        self.sprint.save()
        
        self.authenticate(self.team_leader)
        url = reverse('sprint-complete', kwargs={'pk': self.sprint.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'COMPLETED')


class TaskAPITest(APITestCase):
    """Test task endpoints"""
    
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            title='Test Task',
            description='Task description',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            priority='P1',
            estimated_hours=5
        )
    
    def test_list_tasks(self):
        """Test listing tasks"""
        self.authenticate(self.employee)
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_task_as_team_leader(self):
        """Test team leader can create task"""
        self.authenticate(self.team_leader)
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'New task description',
            'project': self.project.id,
            'assigned_to': self.employee.id,
            'priority': 'P0',
            'estimated_hours': 8
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(title='New Task').count(), 1)
    
    def test_get_my_tasks(self):
        """Test getting tasks assigned to current user"""
        self.authenticate(self.employee)
        url = reverse('task-my-tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task')
    
    def test_get_overdue_tasks(self):
        """Test getting overdue tasks"""
        # Create overdue task
        Task.objects.create(
            title='Overdue Task',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            due_date=timezone.now().date() - timedelta(days=1),
            status='IN_PROGRESS'
        )
        
        self.authenticate(self.employee)
        url = reverse('task-overdue')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_change_task_status(self):
        """Test changing task status"""
        self.authenticate(self.employee)
        url = reverse('task-change-status', kwargs={'pk': self.task.id})
        data = {'status': 'IN_PROGRESS'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'IN_PROGRESS')


class ReviewAPITest(APITestCase):
    """Test review endpoints"""
    
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            title='Task for Review',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='SUBMITTED'
        )
        self.review = Review.objects.create(
            task=self.task,
            submitted_by=self.employee,
            comments='Please review my work'
        )
    
    def test_list_reviews(self):
        """Test listing reviews"""
        self.authenticate(self.reviewer)
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_review(self):
        """Test creating a review"""
        task2 = Task.objects.create(
            title='Another Task',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            status='SUBMITTED'
        )
        
        self.authenticate(self.employee)
        url = reverse('review-list')
        data = {
            'task': task2.id,
            'comments': 'Ready for review'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_assign_reviewer(self):
        """Test assigning a reviewer"""
        self.authenticate(self.team_leader)
        url = reverse('review-assign-reviewer', kwargs={'pk': self.review.id})
        data = {'reviewer_id': self.reviewer.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.status, 'IN_REVIEW')
    
    def test_approve_review(self):
        """Test approving a review"""
        self.review.reviewer = self.reviewer
        self.review.status = 'IN_REVIEW'
        self.review.save()
        
        self.authenticate(self.reviewer)
        url = reverse('review-approve', kwargs={'pk': self.review.id})
        data = {'feedback': 'Looks good!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, 'APPROVED')
    
    def test_request_changes(self):
        """Test requesting changes in review"""
        self.review.reviewer = self.reviewer
        self.review.status = 'IN_REVIEW'
        self.review.save()
        
        self.authenticate(self.reviewer)
        url = reverse('review-request-changes', kwargs={'pk': self.review.id})
        data = {'feedback': 'Please fix the bugs'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, 'CHANGES_REQUESTED')


class AnalyticsAPITest(APITestCase):
    """Test analytics endpoints"""
    
    def test_project_statistics(self):
        """Test project statistics endpoint"""
        self.authenticate(self.admin)
        url = reverse('project-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_projects', response.data)
        self.assertIn('active_projects', response.data)
    
    def test_task_statistics(self):
        """Test task statistics endpoint"""
        self.authenticate(self.admin)
        url = reverse('task-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tasks', response.data)
        self.assertIn('tasks_by_status', response.data)

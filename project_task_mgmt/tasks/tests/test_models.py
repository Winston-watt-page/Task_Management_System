"""
Unit tests for models in the tasks app
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date, timedelta
from tasks.models import (
    User, Team, TeamMember, Project, ProjectMember, Sprint, Task,
    TaskDependency, Review, ReviewComment, Comment, Mention,
    Attachment, Notification, ActivityLog, Report, Analytics
)

User = get_user_model()


@pytest.mark.django_db
class TestUserModel(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
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
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123',
            role='REVIEWER'
        )
    
    def test_user_creation(self):
        """Test user is created successfully"""
        self.assertEqual(self.admin_user.username, 'admin')
        self.assertEqual(self.admin_user.email, 'admin@test.com')
        self.assertEqual(self.admin_user.role, 'ADMIN')
        self.assertTrue(self.admin_user.is_active)
    
    def test_user_str_method(self):
        """Test string representation of user"""
        expected = "admin (Admin)"
        self.assertEqual(str(self.admin_user), expected)
    
    def test_user_is_admin_property(self):
        """Test is_admin property"""
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.team_leader.is_admin)
        self.assertFalse(self.employee.is_admin)
    
    def test_user_is_team_leader_property(self):
        """Test is_team_leader property"""
        self.assertFalse(self.admin_user.is_team_leader)
        self.assertTrue(self.team_leader.is_team_leader)
        self.assertFalse(self.employee.is_team_leader)
    
    def test_user_is_employee_property(self):
        """Test is_employee property"""
        self.assertFalse(self.admin_user.is_employee)
        self.assertTrue(self.team_leader.is_employee)
        self.assertTrue(self.employee.is_employee)
    
    def test_user_is_reviewer_property(self):
        """Test is_reviewer property"""
        self.assertFalse(self.admin_user.is_reviewer)
        self.assertTrue(self.reviewer.is_reviewer)
    
    def test_user_password_hashing(self):
        """Test password is hashed"""
        self.assertNotEqual(self.admin_user.password, 'testpass123')
        self.assertTrue(self.admin_user.check_password('testpass123'))


@pytest.mark.django_db
class TestTeamModel(TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        """Set up test data"""
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.employee1 = User.objects.create_user(
            username='emp1',
            email='emp1@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        self.employee2 = User.objects.create_user(
            username='emp2',
            email='emp2@test.com',
            password='testpass123',
            role='EMPLOYEE'
        )
        self.team = Team.objects.create(
            name='Development Team',
            description='Main development team',
            team_leader=self.team_leader
        )
        self.team.members.add(self.employee1, self.employee2)
    
    def test_team_creation(self):
        """Test team is created successfully"""
        self.assertEqual(self.team.name, 'Development Team')
        self.assertEqual(self.team.team_leader, self.team_leader)
        self.assertEqual(self.team.members.count(), 2)
    
    def test_team_str_method(self):
        """Test string representation of team"""
        self.assertEqual(str(self.team), 'Development Team')
    
    def test_team_member_addition(self):
        """Test adding members to team"""
        new_employee = User.objects.create_user(
            username='emp3',
            email='emp3@test.com',
            password='testpass123'
        )
        self.team.members.add(new_employee)
        self.assertEqual(self.team.members.count(), 3)
        self.assertIn(new_employee, self.team.members.all())


@pytest.mark.django_db
class TestProjectModel(TestCase):
    """Test cases for Project model"""
    
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
            description='A test project',
            team=self.team,
            created_by=self.team_leader,
            start_date=date.today(),
            status='PLANNING'
        )
    
    def test_project_creation(self):
        """Test project is created successfully"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.status, 'PLANNING')
        self.assertEqual(self.project.progress_percentage, 0)
    
    def test_project_str_method(self):
        """Test string representation of project"""
        self.assertEqual(str(self.project), 'Test Project')
    
    def test_project_calculate_progress(self):
        """Test progress calculation"""
        # Create sprint for tasks
        sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
        
        # Create tasks
        employee = User.objects.create_user(
            username='emp',
            email='emp@test.com',
            password='testpass123'
        )
        Task.objects.create(
            project=self.project,
            sprint=sprint,
            title='Task 1',
            assigned_by=self.team_leader,
            status='DONE'
        )
        Task.objects.create(
            project=self.project,
            sprint=sprint,
            title='Task 2',
            assigned_by=self.team_leader,
            status='IN_PROGRESS'
        )
        
        progress = self.project.calculate_progress()
        self.assertEqual(progress, 50)


@pytest.mark.django_db
class TestSprintModel(TestCase):
    """Test cases for Sprint model"""
    
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
            goal='Complete initial features',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
            status='PLANNING'
        )
    
    def test_sprint_creation(self):
        """Test sprint is created successfully"""
        self.assertEqual(self.sprint.name, 'Sprint 1')
        self.assertEqual(self.sprint.status, 'PLANNING')
        self.assertEqual(self.sprint.velocity, 0)
    
    def test_sprint_str_method(self):
        """Test string representation of sprint"""
        expected = "Test Project - Sprint 1"
        self.assertEqual(str(self.sprint), expected)
    
    def test_sprint_calculate_velocity(self):
        """Test velocity calculation"""
        Task.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Task 1',
            assigned_by=self.team_leader,
            status='DONE',
            estimated_hours=8
        )
        Task.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Task 2',
            assigned_by=self.team_leader,
            status='DONE',
            estimated_hours=5
        )
        
        velocity = self.sprint.calculate_velocity()
        self.assertEqual(velocity, 13)


@pytest.mark.django_db
class TestTaskModel(TestCase):
    """Test cases for Task model"""
    
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
            description='A test task',
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN',
            estimated_hours=5
        )
    
    def test_task_creation(self):
        """Test task is created successfully"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.priority, 'P1')
        self.assertEqual(self.task.status, 'OPEN')
        self.assertEqual(self.task.estimated_hours, 5)
    
    def test_task_str_method(self):
        """Test string representation of task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_assignment(self):
        """Test task assignment"""
        self.assertEqual(self.task.assigned_to, self.employee)
        self.assertEqual(self.task.assigned_by, self.team_leader)
    
    def test_task_status_changes(self):
        """Test task status updates"""
        self.task.status = 'IN_PROGRESS'
        self.task.save()
        self.assertEqual(self.task.status, 'IN_PROGRESS')
        
        self.task.status = 'DONE'
        self.task.save()
        self.assertEqual(self.task.status, 'DONE')


@pytest.mark.django_db
class TestReviewModel(TestCase):
    """Test cases for Review model"""
    
    def setUp(self):
        """Set up test data"""
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='lead@test.com',
            password='testpass123',
            role='TEAM_LEADER'
        )
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@test.com',
            password='testpass123',
            role='REVIEWER'
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
            assigned_by=self.team_leader,
            status='SUBMITTED'
        )
        self.review = Review.objects.create(
            task=self.task,
            submitted_by=self.team_leader,
            reviewer=self.reviewer,
            status='PENDING'
        )
    
    def test_review_creation(self):
        """Test review is created successfully"""
        self.assertEqual(self.review.task, self.task)
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.status, 'PENDING')
    
    def test_review_approval(self):
        """Test review approval"""
        self.review.status = 'APPROVED'
        self.review.save()
        self.assertEqual(self.review.status, 'APPROVED')


@pytest.mark.django_db
class TestNotificationModel(TestCase):
    """Test cases for Notification model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            type='TASK_ASSIGNED'
        )
    
    def test_notification_creation(self):
        """Test notification is created successfully"""
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.user, self.user)
        self.assertFalse(self.notification.is_read)
    
    def test_notification_mark_as_read(self):
        """Test marking notification as read"""
        self.notification.is_read = True
        self.notification.save()
        self.assertTrue(self.notification.is_read)

"""
Test cases for models in the tasks app
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from tasks.models import (
    User, Team, Project, ProjectMember, Sprint, Task,
    TaskDependency, Review, ReviewComment, Comment,
    Mention, Attachment, Notification, ActivityLog
)


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='ADMIN',
            first_name='Admin',
            last_name='User'
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
    
    def test_user_creation(self):
        """Test user is created with correct attributes"""
        self.assertEqual(self.admin.username, 'admin')
        self.assertEqual(self.admin.role, 'ADMIN')
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_team_leader)
    
    def test_role_properties(self):
        """Test role property methods"""
        self.assertTrue(self.admin.is_admin)
        self.assertTrue(self.team_leader.is_team_leader)
        self.assertTrue(self.employee.is_employee)
        self.assertFalse(self.employee.is_admin)
    
    def test_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.admin), 'admin (Admin)')
        self.assertEqual(str(self.employee), 'employee (Employee)')


class TeamModelTest(TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        self.leader = User.objects.create_user(
            username='leader',
            password='pass123',
            role='TEAM_LEADER'
        )
        self.team = Team.objects.create(
            name='Development Team',
            description='Backend dev team',
            team_leader=self.leader
        )
    
    def test_team_creation(self):
        """Test team is created correctly"""
        self.assertEqual(self.team.name, 'Development Team')
        self.assertEqual(self.team.team_leader, self.leader)
        # Team model doesn't have is_active field
        self.assertIsNotNone(self.team.created_at)
    
    def test_team_str(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), 'Development Team')


class ProjectModelTest(TestCase):
    """Test cases for Project model"""
    
    def setUp(self):
        self.leader = User.objects.create_user(
            username='leader',
            password='pass123',
            role='TEAM_LEADER'
        )
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.leader
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project description',
            team=self.team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            created_by=self.leader
        )
    
    def test_project_creation(self):
        """Test project creation"""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.team, self.team)
        self.assertEqual(self.project.status, 'PLANNING')
    
    def test_project_progress_calculation(self):
        """Test progress percentage calculation"""
        # Initially no tasks, progress should be 0
        self.assertEqual(self.project.progress_percentage, 0)
        
        # Create some tasks
        employee = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        Task.objects.create(
            title='Task 1',
            project=self.project,
            assigned_to=employee,
            assigned_by=self.leader,
            status='DONE'
        )
        Task.objects.create(
            title='Task 2',
            project=self.project,
            assigned_to=employee,
            assigned_by=self.leader,
            status='IN_PROGRESS'
        )
        
        # Refresh from DB
        self.project.refresh_from_db()
        # 1 out of 2 tasks done = 50%
        self.assertEqual(self.project.progress_percentage, 50)
    
    def test_project_str(self):
        """Test project string representation"""
        self.assertEqual(str(self.project), 'Test Project')


class SprintModelTest(TestCase):
    """Test cases for Sprint model"""
    
    def setUp(self):
        leader = User.objects.create_user(username='leader', password='pass', role='TEAM_LEADER')
        team = Team.objects.create(name='Team', team_leader=leader)
        self.project = Project.objects.create(
            name='Project',
            team=team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            created_by=leader
        )
        self.sprint = Sprint.objects.create(
            name='Sprint 1',
            project=self.project,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=14),
            goal='Complete core features'
        )
    
    def test_sprint_creation(self):
        """Test sprint creation"""
        self.assertEqual(self.sprint.name, 'Sprint 1')
        self.assertEqual(self.sprint.status, 'PLANNING')
    
    def test_sprint_is_active(self):
        """Test sprint active status"""
        self.assertNotEqual(self.sprint.status, 'ACTIVE')
        
        self.sprint.status = 'ACTIVE'
        self.sprint.save()
        self.assertEqual(self.sprint.status, 'ACTIVE')
    
    def test_sprint_str(self):
        """Test sprint string representation"""
        self.assertEqual(str(self.sprint), 'Project - Sprint 1')


class TaskModelTest(TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        self.leader = User.objects.create_user(username='leader', password='pass', role='TEAM_LEADER')
        self.employee = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        team = Team.objects.create(name='Team', team_leader=self.leader)
        self.project = Project.objects.create(
            name='Project',
            team=team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            created_by=self.leader
        )
        self.task = Task.objects.create(
            title='Implement login',
            description='Create login functionality',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.leader,
            priority='P0',
            estimated_hours=8,
            due_date=timezone.now().date() + timedelta(days=7)
        )
    
    def test_task_creation(self):
        """Test task creation"""
        self.assertEqual(self.task.title, 'Implement login')
        self.assertEqual(self.task.status, 'OPEN')
        self.assertEqual(self.task.priority, 'P0')
    
    def test_task_is_overdue(self):
        """Test overdue task detection"""
        # Task due in future - not overdue
        self.assertFalse(self.task.is_overdue)
        
        # Set due date to past
        self.task.due_date = timezone.now().date() - timedelta(days=1)
        self.task.save()
        self.assertTrue(self.task.is_overdue)
        
        # Completed task is never overdue
        self.task.status = 'DONE'
        self.task.save()
        self.assertFalse(self.task.is_overdue)
    
    def test_task_tag_list(self):
        """Test tag list parsing"""
        self.task.tags = 'backend,authentication,urgent'
        self.task.save()
        self.assertEqual(self.task.tag_list, ['backend', 'authentication', 'urgent'])
        
        self.task.tags = ''
        self.task.save()
        self.assertEqual(self.task.tag_list, [])
    
    def test_task_str(self):
        """Test task string representation"""
        self.assertEqual(str(self.task), 'Implement login')


class TaskDependencyModelTest(TestCase):
    """Test cases for TaskDependency model"""
    
    def setUp(self):
        leader = User.objects.create_user(username='leader', password='pass', role='TEAM_LEADER')
        employee = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        team = Team.objects.create(name='Team', team_leader=leader)
        project = Project.objects.create(
            name='Project',
            team=team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            created_by=leader
        )
        self.task1 = Task.objects.create(
            title='Task 1',
            project=project,
            assigned_to=employee,
            assigned_by=leader
        )
        self.task2 = Task.objects.create(
            title='Task 2',
            project=project,
            assigned_to=employee,
            assigned_by=leader
        )
    
    def test_task_dependency_creation(self):
        """Test task dependency creation"""
        dependency = TaskDependency.objects.create(
            task=self.task2,
            depends_on_task=self.task1
        )
        self.assertEqual(dependency.task, self.task2)
        self.assertEqual(dependency.depends_on_task, self.task1)
    
    def test_circular_dependency_prevention(self):
        """Test that circular dependencies are prevented"""
        # Create A depends on B
        TaskDependency.objects.create(task=self.task2, depends_on_task=self.task1)
        
        # Try to create B depends on A (circular)
        with self.assertRaises(ValidationError):
            dep = TaskDependency(task=self.task1, depends_on_task=self.task2)
            dep.full_clean()


class ReviewModelTest(TestCase):
    """Test cases for Review model"""
    
    def setUp(self):
        leader = User.objects.create_user(username='leader', password='pass', role='TEAM_LEADER')
        employee = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        self.reviewer = User.objects.create_user(username='reviewer', password='pass', role='REVIEWER')
        team = Team.objects.create(name='Team', team_leader=leader)
        project = Project.objects.create(
            name='Project',
            team=team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            created_by=leader
        )
        self.task = Task.objects.create(
            title='Task',
            project=project,
            assigned_to=employee,
            assigned_by=leader,
            status='SUBMITTED'
        )
        self.review = Review.objects.create(
            task=self.task,
            submitted_by=employee,
            comments='Please review'
        )
    
    def test_review_creation(self):
        """Test review creation"""
        self.assertEqual(self.review.status, 'PENDING')
        self.assertIsNone(self.review.reviewer)
    
    def test_review_assignment(self):
        """Test assigning reviewer"""
        self.review.reviewer = self.reviewer
        self.review.status = 'IN_REVIEW'
        self.review.save()
        
        self.assertEqual(self.review.reviewer, self.reviewer)
        self.assertEqual(self.review.status, 'IN_REVIEW')
    
    def test_review_str(self):
        """Test review string representation"""
        self.assertIn('Task', str(self.review))


class NotificationModelTest(TestCase):
    """Test cases for Notification model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass', role='EMPLOYEE')
    
    def test_notification_creation(self):
        """Test notification creation"""
        notification = Notification.objects.create(
            user=self.user,
            type='TASK_ASSIGNED',
            title='New Task',
            message='You have been assigned a new task'
        )
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.type, 'TASK_ASSIGNED')
    
    def test_notification_str(self):
        """Test notification string representation"""
        notification = Notification.objects.create(
            user=self.user,
            type='TASK_ASSIGNED',
            title='New Task',
            message='Message'
        )
        # Check the actual format: "TYPE - username"
        self.assertIn('TASK_ASSIGNED', str(notification))
        self.assertIn('user', str(notification))


class CommentModelTest(TestCase):
    """Test cases for Comment model"""
    
    def setUp(self):
        leader = User.objects.create_user(username='leader', password='pass', role='TEAM_LEADER')
        employee = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        team = Team.objects.create(name='Team', team_leader=leader)
        project = Project.objects.create(
            name='Project',
            team=team,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            created_by=leader
        )
        self.task = Task.objects.create(
            title='Task',
            project=project,
            assigned_to=employee,
            assigned_by=leader
        )
        self.user = employee
    
    def test_comment_creation(self):
        """Test comment creation"""
        comment = Comment.objects.create(
            task=self.task,
            user=self.user,
            content='This is a comment'
        )
        self.assertEqual(comment.content, 'This is a comment')
        self.assertEqual(comment.task, self.task)
    
    def test_comment_str(self):
        """Test comment string representation"""
        comment = Comment.objects.create(
            task=self.task,
            user=self.user,
            content='Test comment'
        )
        self.assertIn('emp', str(comment))
        self.assertIn('Task', str(comment))

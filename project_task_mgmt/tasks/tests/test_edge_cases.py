"""
Comprehensive edge case and boundary testing
Tests for validation, error handling, and boundary conditions
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import authenticate
from datetime import timedelta
from tasks.models import (
    User, Team, TeamMember, Project, ProjectMember, Sprint, Task,
    TaskDependency, Review, ReviewComment, Comment,
    Mention, Attachment, Notification, ActivityLog, Report, Analytics
)


class UserEdgeCasesTest(TestCase):
    """Test edge cases for User model"""
    
    def test_user_with_invalid_role(self):
        """Test that invalid role raises ValidationError"""
        user = User(username='testuser', role='INVALID_ROLE')
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_duplicate_username(self):
        """Test that duplicate username raises IntegrityError"""
        User.objects.create_user(username='duplicate', password='pass123')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='duplicate', password='pass456')
    
    def test_duplicate_email_allowed(self):
        """Test that duplicate email is allowed (no unique constraint on email)"""
        User.objects.create_user(username='user1', email='same@test.com', password='pass123')
        user2 = User.objects.create_user(username='user2', email='same@test.com', password='pass456')
        self.assertEqual(user2.email, 'same@test.com')
    
    def test_user_with_empty_password(self):
        """Test user creation with empty password"""
        user = User.objects.create_user(username='emptypass', password='')
        self.assertTrue(user.has_usable_password())
    
    def test_very_long_username(self):
        """Test username length validation"""
        long_username = 'a' * 151  # Django default max_length is 150
        user = User(username=long_username, password='pass123')
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_inactive_user_cannot_login(self):
        """Test that inactive users cannot authenticate"""
        user = User.objects.create_user(username='inactive', password='pass123')
        user.is_active = False
        user.save()
        
        result = authenticate(username='inactive', password='pass123')
        self.assertIsNone(result)
    
    def test_all_role_properties(self):
        """Test all role property methods"""
        admin = User.objects.create_user(username='admin', password='pass', role='ADMIN')
        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_team_leader)
        
        tl = User.objects.create_user(username='tl', password='pass', role='TEAM_LEADER')
        self.assertTrue(tl.is_team_leader)
        self.assertTrue(tl.is_employee)  # Team leaders are also employees
        
        emp = User.objects.create_user(username='emp', password='pass', role='EMPLOYEE')
        self.assertTrue(emp.is_employee)
        
        reviewer = User.objects.create_user(username='rev', password='pass', role='REVIEWER')
        self.assertTrue(reviewer.is_reviewer)


class TeamEdgeCasesTest(TestCase):
    """Test edge cases for Team model"""
    
    def setUp(self):
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
    
    def test_team_requires_leader(self):
        """Test team requires a leader (NOT NULL constraint)"""
        team = Team(name='No Leader Team')
        with self.assertRaises(IntegrityError):
            team.save()
    
    def test_team_with_very_long_name(self):
        """Test team name length validation"""
        long_name = 'a' * 256
        team = Team(name=long_name, team_leader=self.team_leader)
        with self.assertRaises(ValidationError):
            team.full_clean()
    
    def test_team_with_empty_name(self):
        """Test team requires a name"""
        team = Team(name='', team_leader=self.team_leader)
        with self.assertRaises(ValidationError):
            team.full_clean()
    
    def test_multiple_team_memberships(self):
        """Test user can be member of multiple teams"""
        user = User.objects.create_user(username='multi', password='pass123')
        team1 = Team.objects.create(name='Team 1', team_leader=self.team_leader)
        team2 = Team.objects.create(name='Team 2', team_leader=self.team_leader)
        
        team1.members.add(user)
        team2.members.add(user)
        
        self.assertEqual(user.teams.count(), 2)


class ProjectEdgeCasesTest(TestCase):
    """Test edge cases for Project model"""
    
    def setUp(self):
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        self.team = Team.objects.create(name='Test Team', team_leader=self.team_leader)
    
    def test_project_end_date_before_start_date(self):
        """Test project with end date before start date (logically invalid but not enforced)"""
        project = Project.objects.create(
            name='Invalid Dates',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timedelta(days=10)
        )
        # Model doesn't enforce date logic, but it exists
        self.assertLess(project.end_date, project.start_date)
    
    def test_project_progress_with_no_tasks(self):
        """Test progress calculation when project has no tasks"""
        project = Project.objects.create(
            name='No Tasks Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(project.progress_percentage, 0)
    
    def test_project_progress_all_tasks_done(self):
        """Test progress calculation when all tasks complete"""
        project = Project.objects.create(
            name='Complete Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        for i in range(5):
            Task.objects.create(
                title=f'Task {i}',
                project=project,
                assigned_to=self.team_leader,
                assigned_by=self.team_leader,
                priority='P1',
                status='DONE'
            )
        
        project.update_progress()
        self.assertEqual(project.progress_percentage, 100)


class TaskEdgeCasesTest(TestCase):
    """Test edge cases for Task model"""
    
    def setUp(self):
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        self.team = Team.objects.create(name='Test Team', team_leader=self.team_leader)
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
    
    def test_task_with_invalid_priority(self):
        """Test task with invalid priority"""
        task = Task(
            title='Invalid Priority',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='INVALID',
            status='OPEN'
        )
        with self.assertRaises(ValidationError):
            task.full_clean()
    
    def test_task_with_invalid_status(self):
        """Test task with invalid status"""
        task = Task(
            title='Invalid Status',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='INVALID_STATUS'
        )
        with self.assertRaises(ValidationError):
            task.full_clean()
    
    def test_circular_dependency_direct(self):
        """Test direct circular dependency (A -> B -> A)"""
        task_a = Task.objects.create(
            title='Task A',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        task_b = Task.objects.create(
            title='Task B',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        
        # A depends on B
        TaskDependency.objects.create(task=task_a, depends_on_task=task_b)
        
        # Try to make B depend on A (circular)
        dep = TaskDependency(task=task_b, depends_on_task=task_a)
        with self.assertRaises(ValidationError) as cm:
            dep.clean()
        self.assertIn('circular', str(cm.exception).lower())
    
    def test_circular_dependency_indirect(self):
        """Test indirect circular dependency (A -> B -> C -> A)"""
        task_a = Task.objects.create(
            title='Task A',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        task_b = Task.objects.create(
            title='Task B',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        task_c = Task.objects.create(
            title='Task C',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        
        # A -> B -> C
        TaskDependency.objects.create(task=task_a, depends_on_task=task_b)
        TaskDependency.objects.create(task=task_b, depends_on_task=task_c)
        
        # Try to make C -> A (circular)
        dep = TaskDependency(task=task_c, depends_on_task=task_a)
        with self.assertRaises(ValidationError) as cm:
            dep.clean()
        self.assertIn('circular', str(cm.exception).lower())
    
    def test_self_dependency(self):
        """Test task cannot depend on itself"""
        task = Task.objects.create(
            title='Self Dependent',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        
        dep = TaskDependency(task=task, depends_on_task=task)
        with self.assertRaises(ValidationError) as cm:
            dep.clean()
        self.assertIn('itself', str(cm.exception).lower())
    
    def test_task_overdue_calculation(self):
        """Test overdue task detection"""
        # Task with past due date
        past_task = Task.objects.create(
            title='Past Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN',
            due_date=timezone.now().date() - timedelta(days=1)
        )
        self.assertTrue(past_task.is_overdue)
        
        # Task with future due date
        future_task = Task.objects.create(
            title='Future Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN',
            due_date=timezone.now().date() + timedelta(days=1)
        )
        self.assertFalse(future_task.is_overdue)
        
        # Completed task is never overdue
        done_task = Task.objects.create(
            title='Done Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='DONE',
            due_date=timezone.now().date() - timedelta(days=5)
        )
        self.assertFalse(done_task.is_overdue)
    
    def test_task_tag_list_property(self):
        """Test tags parsing from comma-separated string"""
        task = Task.objects.create(
            title='Tagged Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN',
            tags='urgent, backend, api, bug-fix'
        )
        tag_list = task.tag_list  # It's a property, not a method
        self.assertEqual(len(tag_list), 4)
        self.assertIn('urgent', tag_list)
        self.assertIn('backend', tag_list)
    
    def test_task_without_assignee(self):
        """Test task can exist without assignee"""
        task = Task.objects.create(
            title='Unassigned Task',
            project=self.project,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        self.assertIsNone(task.assigned_to)
    
    def test_all_task_priorities(self):
        """Test all valid priority levels"""
        priorities = ['P0', 'P1', 'P2', 'P3']
        for priority in priorities:
            task = Task.objects.create(
                title=f'Task {priority}',
                project=self.project,
                assigned_to=self.team_leader,
                assigned_by=self.team_leader,
                priority=priority,
                status='OPEN'
            )
            self.assertEqual(task.priority, priority)
    
    def test_all_task_statuses(self):
        """Test all valid task status values"""
        statuses = ['OPEN', 'IN_PROGRESS', 'REVIEW', 'DONE', 'CLOSED']
        task = Task.objects.create(
            title='Status Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
        
        for status in statuses:
            task.status = status
            task.save()
            task.refresh_from_db()
            self.assertEqual(task.status, status)


class SprintEdgeCasesTest(TestCase):
    """Test edge cases for Sprint model"""
    
    def setUp(self):
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        self.team = Team.objects.create(name='Test Team', team_leader=self.team_leader)
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90)
        )
    
    def test_sprint_all_statuses(self):
        """Test all sprint status values"""
        statuses = ['PLANNING', 'ACTIVE', 'COMPLETED', 'CANCELLED']
        sprint = Sprint.objects.create(
            name='Test Sprint',
            project=self.project,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=14),
            status='PLANNING'
        )
        
        for status in statuses:
            sprint.status = status
            sprint.save()
            sprint.refresh_from_db()
            self.assertEqual(sprint.status, status)
    
    def test_overlapping_sprints_allowed(self):
        """Test multiple sprints can overlap"""
        sprint1 = Sprint.objects.create(
            name='Sprint 1',
            project=self.project,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=14)
        )
        sprint2 = Sprint.objects.create(
            name='Sprint 2',
            project=self.project,
            start_date=timezone.now().date() + timedelta(days=7),
            end_date=timezone.now().date() + timedelta(days=21)
        )
        self.assertEqual(Sprint.objects.filter(project=self.project).count(), 2)
    
    def test_sprint_velocity_calculation(self):
        """Test sprint velocity calculation"""
        sprint = Sprint.objects.create(
            name='Test Sprint',
            project=self.project,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=14)
        )
        
        # Create tasks with estimated hours
        task1 = Task.objects.create(
            title='Task 1',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='DONE',
            estimated_hours=8,
            sprint=sprint
        )
        task2 = Task.objects.create(
            title='Task 2',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='DONE',
            estimated_hours=5,
            sprint=sprint
        )
        
        velocity = sprint.calculate_velocity()
        self.assertEqual(velocity, 13)  # 8 + 5


class ReviewEdgeCasesTest(TestCase):
    """Test edge cases for Review model"""
    
    def setUp(self):
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        self.reviewer = User.objects.create_user(
            username='reviewer', password='pass123', role='REVIEWER'
        )
        self.team = Team.objects.create(name='Test Team', team_leader=self.team_leader)
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.team_leader,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
    
    def test_review_without_reviewer(self):
        """Test review can be created without assigned reviewer"""
        review = Review.objects.create(
            task=self.task,
            submitted_by=self.team_leader,
            status='PENDING'
        )
        self.assertIsNone(review.reviewer)
    
    def test_review_invalid_status(self):
        """Test review with invalid status"""
        review = Review(
            task=self.task,
            submitted_by=self.team_leader,
            status='INVALID'
        )
        with self.assertRaises(ValidationError):
            review.full_clean()
    
    def test_multiple_reviews_per_task(self):
        """Test task can have multiple reviews"""
        Review.objects.create(
            task=self.task,
            submitted_by=self.team_leader,
            status='PENDING'
        )
        Review.objects.create(
            task=self.task,
            submitted_by=self.team_leader,
            status='PENDING'
        )
        self.assertEqual(self.task.reviews.count(), 2)
    
    def test_review_all_statuses(self):
        """Test all review status values"""
        statuses = ['PENDING', 'IN_REVIEW', 'APPROVED', 'CHANGES_REQUESTED']
        review = Review.objects.create(
            task=self.task,
            submitted_by=self.team_leader,
            reviewer=self.reviewer,
            status='PENDING'
        )
        
        for status in statuses:
            review.status = status
            review.save()
            review.refresh_from_db()
            self.assertEqual(review.status, status)


class NotificationEdgeCasesTest(TestCase):
    """Test edge cases for Notification model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass123')
    
    def test_notification_all_types(self):
        """Test notification type field"""
        types = ['INFO', 'WARNING', 'ERROR', 'SUCCESS']
        for notif_type in types:
            notification = Notification.objects.create(
                user=self.user,
                type=notif_type,
                title=f'{notif_type} Notification',
                message='Test message'
            )
            self.assertEqual(notification.type, notif_type)
    
    def test_bulk_notification_creation(self):
        """Test creating many notifications"""
        notifications = [
            Notification(
                user=self.user,
                title=f'Notification {i}',
                message=f'Message {i}'
            ) for i in range(100)
        ]
        Notification.objects.bulk_create(notifications)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 100)
    
    def test_notification_default_unread(self):
        """Test notifications are unread by default"""
        notification = Notification.objects.create(
            user=self.user,
            title='Test',
            message='Test notification'
        )
        self.assertFalse(notification.is_read)


class CommentEdgeCasesTest(TestCase):
    """Test edge cases for Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass123')
        self.team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        self.team = Team.objects.create(name='Test Team', team_leader=self.team_leader)
        self.project = Project.objects.create(
            name='Test Project',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            assigned_to=self.user,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
    
    def test_comment_with_very_long_content(self):
        """Test comment with very long content"""
        long_content = 'A' * 10000
        comment = Comment.objects.create(
            task=self.task,
            user=self.user,
            content=long_content
        )
        self.assertEqual(len(comment.content), 10000)
    
    def test_threaded_comments(self):
        """Test comment with parent (threading)"""
        parent = Comment.objects.create(
            task=self.task,
            user=self.user,
            content='Parent comment'
        )
        reply = Comment.objects.create(
            task=self.task,
            user=self.team_leader,
            content='Reply to parent',
            parent_comment=parent
        )
        self.assertEqual(reply.parent_comment, parent)


class ValidationEdgeCasesTest(TestCase):
    """Test model validation edge cases"""
    
    def test_project_member_duplicate(self):
        """Test duplicate project member entries"""
        team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        employee = User.objects.create_user(
            username='employee', password='pass123', role='EMPLOYEE'
        )
        team = Team.objects.create(name='Test Team', team_leader=team_leader)
        project = Project.objects.create(
            name='Test Project',
            team=team,
            created_by=team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        ProjectMember.objects.create(project=project, user=employee, role='DEVELOPER')
        
        # Try to add same user again - should raise IntegrityError due to unique_together
        with self.assertRaises(IntegrityError):
            ProjectMember.objects.create(project=project, user=employee, role='TESTER')
    
    def test_activity_log_auto_timestamp(self):
        """Test activity log auto-creates timestamp"""
        user = User.objects.create_user(username='user', password='pass123')
        log = ActivityLog.objects.create(
            user=user,
            entity_type='Task',
            entity_id='123',
            action='CREATED'
        )
        self.assertIsNotNone(log.created_at)
        self.assertLess((timezone.now() - log.created_at).total_seconds(), 5)


class BoundaryValueTest(TestCase):
    """Test boundary value conditions"""
    
    def test_project_progress_boundaries(self):
        """Test project progress at 0% and 100%"""
        team_leader = User.objects.create_user(
            username='leader', password='pass123', role='TEAM_LEADER'
        )
        team = Team.objects.create(name='Test Team', team_leader=team_leader)
        project = Project.objects.create(
            name='Test Project',
            team=team,
            created_by=team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        # 0% - no tasks
        self.assertEqual(project.progress_percentage, 0)
        
        # Create tasks
        for i in range(10):
            Task.objects.create(
                title=f'Task {i}',
                project=project,
                assigned_to=team_leader,
                assigned_by=team_leader,
                priority='P1',
                status='OPEN'
            )
        
        # Still 0%
        project.update_progress()
        self.assertEqual(project.progress_percentage, 0)
        
        # Mark all done
        Task.objects.filter(project=project).update(status='DONE')
        project.update_progress()
        self.assertEqual(project.progress_percentage, 100)

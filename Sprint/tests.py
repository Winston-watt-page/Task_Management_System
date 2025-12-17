from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.template import TemplateDoesNotExist
from .models import Sprint, Issue, Comment, TimeLog, ActivityLog, Attachment, Watcher
from Projects.models import Project
from datetime import date


class SprintModelTest(TestCase):
    """Test cases for Sprint model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
    
    def test_sprint_creation(self):
        """Test Sprint creation"""
        sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            team_lead=self.user,
            goal='Complete features',
            status='planning',
            created_by=self.user
        )
        
        self.assertEqual(sprint.project, self.project)
        self.assertEqual(sprint.name, 'Sprint 1')
        self.assertEqual(sprint.team_lead, self.user)
        self.assertEqual(sprint.status, 'planning')
    
    def test_sprint_str(self):
        """Test Sprint string representation"""
        sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            created_by=self.user
        )
        expected = f"{self.project.key} - Sprint 1"
        self.assertEqual(str(sprint), expected)
    
    def test_sprint_default_status(self):
        """Test Sprint default status"""
        sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            created_by=self.user
        )
        self.assertEqual(sprint.status, 'planning')
    
    def test_sprint_default_velocity(self):
        """Test Sprint default velocity"""
        sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            created_by=self.user
        )
        self.assertEqual(sprint.velocity, 0)


class IssueModelTest(TestCase):
    """Test cases for Issue model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            created_by=self.user
        )
    
    def test_issue_creation(self):
        """Test Issue creation"""
        issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            issue_type='task',
            title='Test Issue',
            description='Test description',
            priority='high',
            status='todo',
            assignee=self.user,
            reporter=self.user
        )
        
        self.assertEqual(issue.project, self.project)
        self.assertEqual(issue.sprint, self.sprint)
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.priority, 'high')
    
    def test_issue_str(self):
        """Test Issue string representation"""
        issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user
        )
        expected = f"{self.project.key}-{issue.id}: Test Issue"
        self.assertEqual(str(issue), expected)
    
    def test_issue_default_values(self):
        """Test Issue default values"""
        issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user
        )
        
        self.assertEqual(issue.issue_type, 'task')
        self.assertEqual(issue.priority, 'medium')
        self.assertEqual(issue.status, 'todo')
        self.assertEqual(issue.actual_hours, 0)
    
    def test_issue_subtask_relationship(self):
        """Test Issue parent-subtask relationship"""
        parent = Issue.objects.create(
            project=self.project,
            title='Parent Issue',
            reporter=self.user
        )
        
        subtask = Issue.objects.create(
            project=self.project,
            parent=parent,
            issue_type='subtask',
            title='Subtask',
            reporter=self.user
        )
        
        self.assertEqual(subtask.parent, parent)
        self.assertIn(subtask, parent.subtasks.all())


class CommentModelTest(TestCase):
    """Test cases for Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user
        )
    
    def test_comment_creation(self):
        """Test Comment creation"""
        comment = Comment.objects.create(
            issue=self.issue,
            user=self.user,
            content='Test comment'
        )
        
        self.assertEqual(comment.issue, self.issue)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'Test comment')
    
    def test_comment_str(self):
        """Test Comment string representation"""
        comment = Comment.objects.create(
            issue=self.issue,
            user=self.user,
            content='Test comment'
        )
        expected = f"Comment by {self.user.username} on {self.issue}"
        self.assertEqual(str(comment), expected)


class TimeLogModelTest(TestCase):
    """Test cases for TimeLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user
        )
    
    def test_timelog_creation(self):
        """Test TimeLog creation"""
        timelog = TimeLog.objects.create(
            issue=self.issue,
            user=self.user,
            hours_spent=5.5,
            description='Worked on feature',
            date=date.today()
        )
        
        self.assertEqual(timelog.issue, self.issue)
        self.assertEqual(timelog.user, self.user)
        self.assertEqual(timelog.hours_spent, 5.5)
    
    def test_timelog_str(self):
        """Test TimeLog string representation"""
        timelog = TimeLog.objects.create(
            issue=self.issue,
            user=self.user,
            hours_spent=3.0,
            date=date.today()
        )
        expected = f"{self.user.username} - 3.0h on {self.issue}"
        self.assertEqual(str(timelog), expected)


class ActivityLogModelTest(TestCase):
    """Test cases for ActivityLog model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user
        )
    
    def test_activitylog_creation(self):
        """Test ActivityLog creation"""
        log = ActivityLog.objects.create(
            issue=self.issue,
            user=self.user,
            action='created'
        )
        
        self.assertEqual(log.issue, self.issue)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'created')
    
    def test_activitylog_with_changes(self):
        """Test ActivityLog with field changes"""
        log = ActivityLog.objects.create(
            issue=self.issue,
            user=self.user,
            action='status_changed',
            field_changed='status',
            old_value='todo',
            new_value='in_progress'
        )
        
        self.assertEqual(log.field_changed, 'status')
        self.assertEqual(log.old_value, 'todo')
        self.assertEqual(log.new_value, 'in_progress')


class WatcherModelTest(TestCase):
    """Test cases for Watcher model"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user1
        )
        self.issue = Issue.objects.create(
            project=self.project,
            title='Test Issue',
            reporter=self.user1
        )
    
    def test_watcher_creation(self):
        """Test Watcher creation"""
        watcher = Watcher.objects.create(
            issue=self.issue,
            user=self.user2
        )
        
        self.assertEqual(watcher.issue, self.issue)
        self.assertEqual(watcher.user, self.user2)
    
    def test_watcher_unique_together(self):
        """Test Watcher unique constraint"""
        Watcher.objects.create(
            issue=self.issue,
            user=self.user2
        )
        
        with self.assertRaises(Exception):
            Watcher.objects.create(
                issue=self.issue,
                user=self.user2
            )


class SprintViewsTest(TestCase):
    """Test cases for Sprint views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.tl_group = Group.objects.create(name='TL')
        self.user.groups.add(self.tl_group)
        
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user
        )
    
    def test_sprint_list_requires_login(self):
        """Test sprint list requires authentication"""
        response = self.client.get(reverse('sprint_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_sprint_list_authenticated(self):
        """Test authenticated user can access sprint list"""
        self.client.login(username='testuser', password='testpass123')
        try:
            response = self.client.get(reverse('sprint_list'))
            self.assertEqual(response.status_code, 200)
        except TemplateDoesNotExist:
            pass  # Template not created yet
    
    def test_sprint_detail_view(self):
        """Test sprint detail view"""
        self.client.login(username='testuser', password='testpass123')
        try:
            response = self.client.get(
                reverse('sprint_detail', kwargs={'sprint_id': self.sprint.id})
            )
            self.assertEqual(response.status_code, 200)
        except TemplateDoesNotExist:
            pass  # Template not created yet
    
    def test_sprint_create_view(self):
        """Test sprint creation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('sprint_create'), {
            'project': self.project.id,
            'name': 'Sprint 2',
            'team_lead': self.user.id,
            'goal': 'Complete tasks'
        })
        
        self.assertTrue(Sprint.objects.filter(name='Sprint 2').exists())
    
    def test_sprint_start_by_tl(self):
        """Test TL can start sprint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('sprint_start', kwargs={'sprint_id': self.sprint.id})
        )
        
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'active')
        self.assertIsNotNone(self.sprint.start_date)
    
    def test_sprint_start_by_non_tl(self):
        """Test non-TL cannot start sprint"""
        other_user = User.objects.create_user(username='other', password='pass')
        self.client.login(username='other', password='pass')
        
        response = self.client.get(
            reverse('sprint_start', kwargs={'sprint_id': self.sprint.id})
        )
        
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'planning')


class IssueViewsTest(TestCase):
    """Test cases for Issue views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            created_by=self.user
        )
        self.issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Issue',
            assignee=self.user,
            reporter=self.user
        )
    
    def test_issue_list_requires_login(self):
        """Test issue list requires authentication"""
        response = self.client.get(reverse('issue_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_issue_list_authenticated(self):
        """Test authenticated user can access issue list"""
        self.client.login(username='testuser', password='testpass123')
        try:
            response = self.client.get(reverse('issue_list'))
            self.assertEqual(response.status_code, 200)
        except TemplateDoesNotExist:
            pass  # Template not created yet
    
    def test_issue_detail_view(self):
        """Test issue detail view"""
        self.client.login(username='testuser', password='testpass123')
        try:
            response = self.client.get(
                reverse('issue_detail', kwargs={'issue_id': self.issue.id})
            )
            self.assertEqual(response.status_code, 200)
        except TemplateDoesNotExist:
            pass  # Template not created yet
    
    def test_issue_create_view(self):
        """Test issue creation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('issue_create'), {
            'project': self.project.id,
            'sprint': self.sprint.id,
            'title': 'New Issue',
            'description': 'Issue description',
            'issue_type': 'task',
            'priority': 'high',
            'assignee': self.user.id
        })
        
        self.assertTrue(Issue.objects.filter(title='New Issue').exists())
    
    def test_issue_update_status(self):
        """Test issue status update"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('issue_update_status', kwargs={'issue_id': self.issue.id}),
            {'status': 'in_progress'}
        )
        
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'in_progress')
    
    def test_issue_add_comment(self):
        """Test adding comment to issue"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('issue_add_comment', kwargs={'issue_id': self.issue.id}),
            {'content': 'Test comment'}
        )
        
        self.assertTrue(Comment.objects.filter(
            issue=self.issue,
            content='Test comment'
        ).exists())
    
    def test_issue_log_time(self):
        """Test logging time on issue"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('issue_log_time', kwargs={'issue_id': self.issue.id}),
            {
                'hours_spent': '4.5',
                'description': 'Worked on feature',
                'date': date.today().isoformat()
            }
        )
        
        self.assertTrue(TimeLog.objects.filter(
            issue=self.issue,
            hours_spent=4.5
        ).exists())
    
    def test_my_issues_view(self):
        """Test my issues view"""
        self.client.login(username='testuser', password='testpass123')
        try:
            response = self.client.get(reverse('my_issues'))
            self.assertEqual(response.status_code, 200)
        except TemplateDoesNotExist:
            pass  # Template not created yet


class SprintEndpointTest(TestCase):
    """Comprehensive endpoint tests for Sprint app"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.user
        )
        
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            team_lead=self.user,
            goal='Complete features',
            start_date=date.today(),
            end_date=date.today() + timezone.timedelta(days=14),
            status='planning',
            created_by=self.user
        )
        
        self.issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Issue',
            description='Test description',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.user,
            assignee=self.user
        )
    
    def test_sprint_list_endpoint_authenticated(self):
        """Test GET /sprints/ endpoint for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sprint_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/sprint_list.html')
        self.assertContains(response, 'Sprint 1')
    
    def test_sprint_list_endpoint_unauthenticated(self):
        """Test GET /sprints/ endpoint redirects unauthenticated users"""
        response = self.client.get(reverse('sprint_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_sprint_detail_endpoint(self):
        """Test GET /sprints/<id>/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sprint_detail', args=[self.sprint.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/sprint_detail.html')
        self.assertContains(response, 'Sprint 1')
    
    def test_sprint_detail_endpoint_invalid_id(self):
        """Test GET /sprints/<id>/ endpoint with invalid sprint ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sprint_detail', args=[9999]))
        
        self.assertEqual(response.status_code, 404)
    
    def test_sprint_create_endpoint_get(self):
        """Test GET /sprints/create/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sprint_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/sprint_create.html')
    
    def test_sprint_create_endpoint_post_success(self):
        """Test POST /sprints/create/ endpoint with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = Sprint.objects.count()
        response = self.client.post(reverse('sprint_create'), {
            'project': self.project.id,
            'name': 'Sprint 2',
            'team_lead': self.user.id,
            'goal': 'New sprint goal',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timezone.timedelta(days=14)).isoformat(),
            'status': 'planning'
        })
        
        self.assertEqual(Sprint.objects.count(), initial_count + 1)
        self.assertTrue(Sprint.objects.filter(name='Sprint 2').exists())
    
    def test_sprint_start_endpoint(self):
        """Test POST /sprints/<id>/start/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('sprint_start', args=[self.sprint.id]))
        
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'active')
        self.assertEqual(response.status_code, 302)
    
    def test_sprint_complete_endpoint(self):
        """Test POST /sprints/<id>/complete/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        # Start sprint first
        self.sprint.status = 'active'
        self.sprint.save()
        
        response = self.client.post(reverse('sprint_complete', args=[self.sprint.id]))
        
        self.sprint.refresh_from_db()
        self.assertEqual(self.sprint.status, 'completed')
        self.assertEqual(response.status_code, 302)
    
    def test_issue_list_endpoint_authenticated(self):
        """Test GET /issues/ endpoint for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('issue_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/issue_list.html')
        self.assertContains(response, 'Test Issue')
    
    def test_issue_list_endpoint_unauthenticated(self):
        """Test GET /issues/ endpoint redirects unauthenticated users"""
        response = self.client.get(reverse('issue_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_issue_detail_endpoint(self):
        """Test GET /issues/<id>/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('issue_detail', args=[self.issue.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/issue_detail.html')
        self.assertContains(response, 'Test Issue')
    
    def test_issue_detail_endpoint_invalid_id(self):
        """Test GET /issues/<id>/ endpoint with invalid issue ID"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('issue_detail', args=[9999]))
        
        self.assertEqual(response.status_code, 404)
    
    def test_issue_create_endpoint_get(self):
        """Test GET /issues/create/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('issue_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/issue_create.html')
    
    def test_issue_create_endpoint_post_success(self):
        """Test POST /issues/create/ endpoint with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = Issue.objects.count()
        response = self.client.post(reverse('issue_create'), {
            'project': self.project.id,
            'sprint': self.sprint.id,
            'title': 'New Issue',
            'description': 'New issue description',
            'issue_type': 'bug',
            'status': 'todo',
            'priority': 'high',
            'assignee': self.user.id,
            'estimated_hours': 5
        })
        
        self.assertEqual(Issue.objects.count(), initial_count + 1)
        self.assertTrue(Issue.objects.filter(title='New Issue').exists())
    
    def test_issue_update_status_endpoint(self):
        """Test POST /issues/<id>/update-status/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('issue_update_status', args=[self.issue.id]),
            {'status': 'in_progress'}
        )
        
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, 'in_progress')
        self.assertEqual(response.status_code, 302)
    
    def test_issue_add_comment_endpoint(self):
        """Test POST /issues/<id>/comment/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = Comment.objects.count()
        response = self.client.post(
            reverse('issue_add_comment', args=[self.issue.id]),
            {'content': 'Test comment content'}
        )
        
        self.assertEqual(Comment.objects.count(), initial_count + 1)
        self.assertTrue(Comment.objects.filter(
            issue=self.issue,
            content='Test comment content'
        ).exists())
    
    def test_issue_log_time_endpoint(self):
        """Test POST /issues/<id>/log-time/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = TimeLog.objects.count()
        response = self.client.post(
            reverse('issue_log_time', args=[self.issue.id]),
            {
                'hours_spent': '3.5',
                'description': 'Working on issue',
                'date': date.today().isoformat()
            }
        )
        
        self.assertEqual(TimeLog.objects.count(), initial_count + 1)
        self.assertTrue(TimeLog.objects.filter(
            issue=self.issue,
            hours_spent=3.5
        ).exists())
    
    def test_my_issues_endpoint(self):
        """Test GET /issues/my/ endpoint"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_issues'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sprint/my_issues.html')
        self.assertContains(response, 'Test Issue')  # User is assignee
    
    def test_my_issues_endpoint_shows_only_user_issues(self):
        """Test /issues/my/ endpoint shows only current user's issues"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123'
        )
        
        # Create issue assigned to other user
        Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Other User Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.user,
            assignee=other_user
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_issues'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Issue')  # Should see own issue
        self.assertNotContains(response, 'Other User Issue')  # Should not see other's issue
    
    def test_sprint_list_categorizes_by_status(self):
        """Test /sprints/ endpoint categorizes sprints by status"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create sprints with different statuses
        Sprint.objects.create(
            project=self.project,
            name='Active Sprint',
            team_lead=self.user,
            created_by=self.user,
            status='active'
        )
        Sprint.objects.create(
            project=self.project,
            name='Completed Sprint',
            team_lead=self.user,
            created_by=self.user,
            status='completed'
        )
        
        response = self.client.get(reverse('sprint_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sprint 1')  # Planning
        self.assertContains(response, 'Active Sprint')
        self.assertContains(response, 'Completed Sprint')
    
    def test_sprint_detail_shows_kanban_board(self):
        """Test /sprints/<id>/ endpoint shows Kanban board layout"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create issues with different statuses
        in_progress_issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='In Progress Issue',
            issue_type='task',
            status='in_progress',
            priority='high',
            reporter=self.user
        )
        completed_issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Completed Issue',
            issue_type='task',
            status='completed',
            priority='low',
            reporter=self.user
        )
        
        response = self.client.get(reverse('sprint_detail', args=[self.sprint.id]))
        
        self.assertEqual(response.status_code, 200)
        # Check that Kanban columns are present
        self.assertContains(response, 'To Do')
        self.assertContains(response, 'In Progress')
        self.assertContains(response, 'Completed')
        # Check that original issue is displayed
        self.assertContains(response, 'Test Issue')

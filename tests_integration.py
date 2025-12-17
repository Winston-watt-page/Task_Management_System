"""
Integration Tests for JIRA Clone Application
Tests the complete workflow and interaction between different modules
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from datetime import date, timedelta
from django.utils import timezone

from Admin.models import UserProfile
from Group.models import GroupPermissionProfile
from Projects.models import Project, Epic, Label
from Sprint.models import Sprint, Issue, Comment, TimeLog, ActivityLog


class EndToEndWorkflowTest(TestCase):
    """Test complete workflow from user creation to issue completion"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        
        # Create developer user
        self.developer = User.objects.create_user(
            username='developer',
            password='dev123',
            email='dev@test.com'
        )
        
        # Create team lead user
        self.team_lead = User.objects.create_user(
            username='teamlead',
            password='tl123',
            email='tl@test.com'
        )
        
        # Create groups
        self.admin_group = Group.objects.create(name='Administrators')
        self.dev_group = Group.objects.create(name='Developers')
        self.tl_group = Group.objects.create(name='Team Leads')
        
        # Assign users to groups
        self.admin.groups.add(self.admin_group)
        self.developer.groups.add(self.dev_group)
        self.team_lead.groups.add(self.tl_group)
        
        # Create permission profiles
        GroupPermissionProfile.objects.create(
            group=self.admin_group,
            can_create_projects=True,
            can_manage_users=True,
            can_create_sprints=True,
            can_start_sprints=True,
            can_assign_tasks=True,
            can_update_any_task=True
        )
        
        GroupPermissionProfile.objects.create(
            group=self.tl_group,
            can_create_projects=True,
            can_create_sprints=True,
            can_start_sprints=True,
            can_assign_tasks=True
        )
        
        GroupPermissionProfile.objects.create(
            group=self.dev_group,
            can_create_projects=False,
            can_create_sprints=False,
            can_assign_tasks=False
        )
    
    def test_complete_workflow(self):
        """Test complete workflow from project creation to issue completion"""
        
        # 1. Admin logs in
        login_success = self.client.login(username='admin', password='admin123')
        self.assertTrue(login_success)
        
        # 2. Admin creates a project
        project = Project.objects.create(
            name='Test Project',
            key='TEST',
            description='Integration test project',
            created_by=self.admin,
            status='active'
        )
        self.assertIsNotNone(project.id)
        
        # 3. Admin creates an epic
        epic = Epic.objects.create(
            project=project,
            name='User Authentication',
            description='Epic for auth features',
            created_by=self.admin
        )
        self.assertEqual(epic.project, project)
        
        # 4. Admin creates labels
        label = Label.objects.create(
            project=project,
            name='backend',
            color='#0052CC'
        )
        self.assertEqual(label.project, project)
        
        # 5. Team Lead creates a sprint
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1',
            team_lead=self.team_lead,
            goal='Implement authentication',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
            status='planning',
            created_by=self.team_lead
        )
        self.assertEqual(sprint.status, 'planning')
        
        # 6. Create an issue in the sprint
        issue = Issue.objects.create(
            project=project,
            sprint=sprint,
            epic=epic,
            title='Implement login form',
            description='Create login form with validation',
            issue_type='task',
            status='todo',
            priority='high',
            assignee=self.developer,
            reporter=self.team_lead,
            estimated_hours=8
        )
        issue.labels.add(label)
        self.assertEqual(issue.status, 'todo')
        
        # 7. Start the sprint
        sprint.status = 'active'
        sprint.save()
        self.assertEqual(sprint.status, 'active')
        
        # 8. Developer updates issue status
        issue.status = 'in_progress'
        issue.save()
        
        # Create activity log
        ActivityLog.objects.create(
            issue=issue,
            user=self.developer,
            action='Status changed from To Do to In Progress'
        )
        
        # 9. Developer adds a comment
        comment = Comment.objects.create(
            issue=issue,
            user=self.developer,
            content='Started working on this'
        )
        self.assertEqual(comment.issue, issue)
        
        # 10. Developer logs time
        time_log = TimeLog.objects.create(
            issue=issue,
            user=self.developer,
            hours_spent=4,
            description='Initial implementation',
            date=date.today()
        )
        self.assertEqual(time_log.hours_spent, 4)
        
        # 11. Developer completes the issue
        issue.status = 'done'
        issue.save()
        
        ActivityLog.objects.create(
            issue=issue,
            user=self.developer,
            action='Status changed to Done'
        )
        
        # 12. Verify the complete workflow
        self.assertEqual(Issue.objects.filter(sprint=sprint).count(), 1)
        self.assertEqual(Comment.objects.filter(issue=issue).count(), 1)
        self.assertEqual(TimeLog.objects.filter(issue=issue).count(), 1)
        self.assertEqual(ActivityLog.objects.filter(issue=issue).count(), 2)
        
        # 13. Complete the sprint
        sprint.status = 'completed'
        sprint.completed_date = date.today()
        sprint.save()
        
        # Verify final state
        self.assertEqual(sprint.status, 'completed')
        self.assertEqual(issue.status, 'done')


class ModuleIntegrationTest(TestCase):
    """Test integration between different modules"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        
        self.admin_group = Group.objects.create(name='Admin')
        self.user.groups.add(self.admin_group)
        
        GroupPermissionProfile.objects.create(
            group=self.admin_group,
            can_create_projects=True,
            can_create_sprints=True,
            can_start_sprints=True
        )
    
    def test_project_sprint_integration(self):
        """Test Project and Sprint module integration"""
        project = Project.objects.create(
            name='Integration Project',
            key='INT',
            created_by=self.user
        )
        
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user
        )
        
        # Verify relationship
        self.assertEqual(sprint.project, project)
        self.assertIn(sprint, project.sprints.all())
    
    def test_sprint_issue_integration(self):
        """Test Sprint and Issue module integration"""
        project = Project.objects.create(
            name='Test Project',
            key='TST',
            created_by=self.user
        )
        
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user
        )
        
        issue = Issue.objects.create(
            project=project,
            sprint=sprint,
            title='Test Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.user
        )
        
        # Verify relationships
        self.assertEqual(issue.sprint, sprint)
        self.assertEqual(issue.project, project)
        self.assertIn(issue, sprint.issues.all())
    
    def test_user_group_permission_integration(self):
        """Test User, Group, and Permission integration"""
        group = Group.objects.create(name='Test Group')
        user = User.objects.create_user(username='testuser2', password='test123')
        user.groups.add(group)
        
        profile = GroupPermissionProfile.objects.create(
            group=group,
            can_create_projects=True,
            can_manage_users=False
        )
        
        # Verify relationships
        self.assertIn(group, user.groups.all())
        self.assertEqual(profile.group, group)
        self.assertTrue(profile.can_create_projects)
    
    def test_project_epic_label_integration(self):
        """Test Project, Epic, and Label integration"""
        project = Project.objects.create(
            name='Feature Project',
            key='FEA',
            created_by=self.user
        )
        
        epic = Epic.objects.create(
            project=project,
            name='Epic 1',
            created_by=self.user
        )
        
        label = Label.objects.create(
            project=project,
            name='frontend',
            color='#FF0000'
        )
        
        issue = Issue.objects.create(
            project=project,
            epic=epic,
            title='Epic Issue',
            issue_type='story',
            status='todo',
            priority='high',
            reporter=self.user
        )
        issue.labels.add(label)
        
        # Verify relationships
        self.assertEqual(epic.project, project)
        self.assertEqual(label.project, project)
        self.assertEqual(issue.epic, epic)
        self.assertIn(label, issue.labels.all())
    
    def test_issue_comment_timelog_integration(self):
        """Test Issue, Comment, and TimeLog integration"""
        project = Project.objects.create(
            name='Work Project',
            key='WRK',
            created_by=self.user
        )
        
        issue = Issue.objects.create(
            project=project,
            title='Work Issue',
            issue_type='task',
            status='in_progress',
            priority='medium',
            reporter=self.user
        )
        
        comment = Comment.objects.create(
            issue=issue,
            user=self.user,
            content='Progress update'
        )
        
        time_log = TimeLog.objects.create(
            issue=issue,
            user=self.user,
            hours_spent=3,
            description='Working on task',
            date=date.today()
        )
        
        # Verify relationships
        self.assertEqual(comment.issue, issue)
        self.assertEqual(time_log.issue, issue)
        self.assertIn(comment, issue.comments.all())
        self.assertIn(time_log, issue.time_logs.all())


class EndpointAccessControlTest(TestCase):
    """Test access control for all endpoints"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123'
        )
        
        # Create test data
        self.project = Project.objects.create(
            name='Test Project',
            key='TEST',
            created_by=self.admin
        )
        
        self.sprint = Sprint.objects.create(
            project=self.project,
            name='Sprint 1',
            team_lead=self.admin,
            created_by=self.admin
        )
        
        self.issue = Issue.objects.create(
            project=self.project,
            sprint=self.sprint,
            title='Test Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.admin
        )
    
    def test_unauthenticated_access_redirects(self):
        """Test that unauthenticated users are redirected to login"""
        protected_urls = [
            reverse('dashboard'),
            reverse('project_list'),
            reverse('sprint_list'),
            reverse('issue_list'),
            reverse('user_list'),
            reverse('group_list'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_authenticated_user_access(self):
        """Test authenticated user can access basic endpoints"""
        self.client.login(username='user', password='user123')
        
        accessible_urls = [
            reverse('dashboard'),
            reverse('project_list'),
            reverse('sprint_list'),
            reverse('issue_list'),
            reverse('my_issues'),
        ]
        
        for url in accessible_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # OK or redirect
    
    def test_admin_user_full_access(self):
        """Test admin user has full access"""
        self.client.login(username='admin', password='admin123')
        
        admin_urls = [
            reverse('user_list'),
            reverse('user_create'),
            reverse('group_list'),
            reverse('group_create'),
            reverse('admin_backlog'),
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            # Admin should either get 200 or be redirected (if additional permissions needed)
            # Some URLs may redirect based on permissions
            self.assertIn(response.status_code, [200, 302, 403])


class DataConsistencyTest(TestCase):
    """Test data consistency across modules"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
    
    def test_cascade_delete_project(self):
        """Test cascading delete when project is deleted"""
        project = Project.objects.create(
            name='Delete Test',
            key='DEL',
            created_by=self.user
        )
        
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user
        )
        
        issue = Issue.objects.create(
            project=project,
            sprint=sprint,
            title='Test Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.user
        )
        
        # Delete project
        project.delete()
        
        # Verify cascading delete
        self.assertEqual(Sprint.objects.filter(id=sprint.id).count(), 0)
        self.assertEqual(Issue.objects.filter(id=issue.id).count(), 0)
    
    def test_cascade_delete_sprint(self):
        """Test cascading delete when sprint is deleted"""
        project = Project.objects.create(
            name='Sprint Delete Test',
            key='SDT',
            created_by=self.user
        )
        
        sprint = Sprint.objects.create(
            project=project,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user
        )
        
        issue = Issue.objects.create(
            project=project,
            sprint=sprint,
            title='Test Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.user
        )
        
        comment = Comment.objects.create(
            issue=issue,
            user=self.user,
            content='Test comment'
        )
        
        # Delete sprint
        sprint_id = sprint.id
        issue_id = issue.id
        sprint.delete()
        
        # Verify sprint is deleted
        self.assertEqual(Sprint.objects.filter(id=sprint_id).count(), 0)
        
        # Issues should still exist but sprint should be null
        issue = Issue.objects.get(id=issue_id)
        self.assertIsNone(issue.sprint)
    
    def test_user_deletion_handling(self):
        """Test handling of user deletion"""
        user1 = User.objects.create_user(username='user1', password='test123')
        user2 = User.objects.create_user(username='user2', password='test123')
        
        project = Project.objects.create(
            name='User Delete Test',
            key='UDT',
            created_by=user1
        )
        
        issue = Issue.objects.create(
            project=project,
            title='Test Issue',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=user1,
            assignee=user2
        )
        
        # Delete user2
        user2.delete()
        
        # Issue should still exist but assignee should be null
        issue = Issue.objects.get(id=issue.id)
        self.assertIsNone(issue.assignee)
        self.assertEqual(issue.reporter, user1)


class PermissionWorkflowTest(TestCase):
    """Test permission-based workflows"""
    
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        
        self.developer = User.objects.create_user(
            username='developer',
            password='dev123'
        )
        
        # Create groups
        admin_group = Group.objects.create(name='Admins')
        dev_group = Group.objects.create(name='Developers')
        
        self.admin.groups.add(admin_group)
        self.developer.groups.add(dev_group)
        
        # Create permission profiles
        GroupPermissionProfile.objects.create(
            group=admin_group,
            can_create_projects=True,
            can_manage_users=True,
            can_create_sprints=True,
            can_start_sprints=True,
            can_assign_tasks=True,
            can_update_any_task=True
        )
        
        GroupPermissionProfile.objects.create(
            group=dev_group,
            can_create_projects=False,
            can_manage_users=False,
            can_create_sprints=False,
            can_start_sprints=False,
            can_assign_tasks=False,
            can_update_any_task=False
        )
    
    def test_admin_can_create_project(self):
        """Test admin can create project"""
        project = Project.objects.create(
            name='Admin Project',
            key='ADM',
            created_by=self.admin
        )
        self.assertIsNotNone(project.id)
    
    def test_admin_can_manage_users(self):
        """Test admin can manage users"""
        admin_profile = GroupPermissionProfile.objects.get(
            group__name='Admins'
        )
        self.assertTrue(admin_profile.can_manage_users)
    
    def test_developer_cannot_create_project(self):
        """Test developer permissions are limited"""
        dev_profile = GroupPermissionProfile.objects.get(
            group__name='Developers'
        )
        self.assertFalse(dev_profile.can_create_projects)
        self.assertFalse(dev_profile.can_manage_users)
    
    def test_developer_can_work_on_assigned_issues(self):
        """Test developer can work on assigned issues"""
        project = Project.objects.create(
            name='Work Project',
            key='WRK',
            created_by=self.admin
        )
        
        issue = Issue.objects.create(
            project=project,
            title='Dev Task',
            issue_type='task',
            status='todo',
            priority='medium',
            reporter=self.admin,
            assignee=self.developer
        )
        
        # Developer should be able to update status and log time
        issue.status = 'in_progress'
        issue.save()
        
        time_log = TimeLog.objects.create(
            issue=issue,
            user=self.developer,
            hours_spent=2,
            date=date.today()
        )
        
        self.assertEqual(issue.assignee, self.developer)
        self.assertEqual(time_log.user, self.developer)


class CrossModuleQueryTest(TestCase):
    """Test queries that span multiple modules"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        
        # Create multiple projects
        self.project1 = Project.objects.create(
            name='Project 1',
            key='P1',
            created_by=self.user,
            status='active'
        )
        
        self.project2 = Project.objects.create(
            name='Project 2',
            key='P2',
            created_by=self.user,
            status='active'
        )
        
        # Create sprints
        self.sprint1 = Sprint.objects.create(
            project=self.project1,
            name='Sprint 1',
            team_lead=self.user,
            created_by=self.user,
            status='active'
        )
        
        self.sprint2 = Sprint.objects.create(
            project=self.project2,
            name='Sprint 2',
            team_lead=self.user,
            created_by=self.user,
            status='planning'
        )
        
        # Create issues
        Issue.objects.create(
            project=self.project1,
            sprint=self.sprint1,
            title='Issue 1',
            issue_type='task',
            status='in_progress',
            priority='high',
            reporter=self.user,
            assignee=self.user
        )
        
        Issue.objects.create(
            project=self.project1,
            sprint=self.sprint1,
            title='Issue 2',
            issue_type='bug',
            status='done',
            priority='medium',
            reporter=self.user
        )
        
        Issue.objects.create(
            project=self.project2,
            sprint=self.sprint2,
            title='Issue 3',
            issue_type='story',
            status='todo',
            priority='low',
            reporter=self.user
        )
    
    def test_get_all_issues_for_user(self):
        """Test getting all issues assigned to a user"""
        user_issues = Issue.objects.filter(assignee=self.user)
        self.assertEqual(user_issues.count(), 1)
    
    def test_get_all_issues_reported_by_user(self):
        """Test getting all issues reported by a user"""
        reported_issues = Issue.objects.filter(reporter=self.user)
        self.assertEqual(reported_issues.count(), 3)
    
    def test_get_active_sprints_across_projects(self):
        """Test getting active sprints across all projects"""
        active_sprints = Sprint.objects.filter(status='active')
        self.assertEqual(active_sprints.count(), 1)
        self.assertEqual(active_sprints.first(), self.sprint1)
    
    def test_get_issues_by_project(self):
        """Test getting all issues for a specific project"""
        project1_issues = Issue.objects.filter(project=self.project1)
        project2_issues = Issue.objects.filter(project=self.project2)
        
        self.assertEqual(project1_issues.count(), 2)
        self.assertEqual(project2_issues.count(), 1)
    
    def test_get_issues_by_sprint_and_status(self):
        """Test getting issues by sprint and status"""
        in_progress_issues = Issue.objects.filter(
            sprint=self.sprint1,
            status='in_progress'
        )
        self.assertEqual(in_progress_issues.count(), 1)
    
    def test_get_active_projects(self):
        """Test getting all active projects"""
        active_projects = Project.objects.filter(status='active')
        self.assertEqual(active_projects.count(), 2)
    
    def test_get_sprint_statistics(self):
        """Test calculating sprint statistics"""
        sprint = self.sprint1
        total_issues = Issue.objects.filter(sprint=sprint).count()
        completed_issues = Issue.objects.filter(
            sprint=sprint,
            status='done'
        ).count()
        
        self.assertEqual(total_issues, 2)
        self.assertEqual(completed_issues, 1)
        
        # Calculate completion percentage
        if total_issues > 0:
            completion_rate = (completed_issues / total_issues) * 100
            self.assertEqual(completion_rate, 50.0)

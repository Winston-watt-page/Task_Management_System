from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, Team, TeamMember, Project, ProjectMember, Sprint, Task, TaskDependency,
    Review, ReviewComment, Comment, Mention, Attachment, Notification, ActivityLog,
    Report, Analytics
)
from .serializers import (
    UserSerializer, UserListSerializer, LoginSerializer, TeamSerializer, TeamMemberSerializer,
    ProjectSerializer, ProjectMemberSerializer, SprintSerializer,
    TaskSerializer, TaskDependencySerializer, ReviewSerializer,
    ReviewCommentSerializer, CommentSerializer, MentionSerializer,
    AttachmentSerializer, NotificationSerializer, ActivityLogSerializer,
    ProjectStatisticsSerializer, SprintStatisticsSerializer,
    TaskStatisticsSerializer, EmployeePerformanceSerializer,
    ReportSerializer, AnalyticsSerializer
)
from .permissions import (
    IsAdmin, IsTeamLeader, IsEmployee, IsReviewer,
    CanManageProject, CanManageTask, CanManageReview
)
import re


# Authentication Views

@api_view(['POST'])
@permission_classes([AllowAny])
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# User ViewSet

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'role']
    ordering = ['username']
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def team_leaders(self, request):
        """Get list of team leaders"""
        team_leaders = User.objects.filter(role='TEAM_LEADER')
        serializer = UserListSerializer(team_leaders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def employees(self, request):
        """Get list of employees"""
        employees = User.objects.filter(role__in=['EMPLOYEE', 'TEAM_LEADER'])
        serializer = UserListSerializer(employees, many=True)
        return Response(serializer.data)


# Team ViewSet

class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team model"""
    
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsTeamLeader]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            team.members.add(user)
            return Response({'detail': f'{user.username} added to team.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a member from the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            team.members.remove(user)
            return Response({'detail': f'{user.username} removed from team.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


# Project ViewSet

class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project model"""
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [CanManageProject]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'created_at']
    filterset_fields = ['status', 'team']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        log_activity(self.request.user, 'Project', serializer.instance.id, 'CREATED')
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        # Filter projects where user is team leader, team member, or project member
        return Project.objects.filter(
            Q(team__team_leader=user) | Q(team__members=user) | Q(members__user=user)
        ).distinct()
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get project summary with statistics"""
        project = self.get_object()
        tasks = project.tasks.all()
        
        return Response({
            'project': ProjectSerializer(project).data,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='DONE').count(),
            'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
            'open_tasks': tasks.filter(status__in=['OPEN', 'IN_PROGRESS']).count(),
            'total_sprints': project.sprints.count(),
            'active_sprints': project.sprints.filter(status='ACTIVE').count(),
            'progress_percentage': project.progress_percentage,
        })


# Project Member ViewSet

class ProjectMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for ProjectMember model"""
    
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsTeamLeader]
    filterset_fields = ['project', 'user', 'role']


# Sprint ViewSet

class SprintViewSet(viewsets.ModelViewSet):
    """ViewSet for Sprint model"""
    
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    permission_classes = [CanManageProject]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'goal']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    filterset_fields = ['status', 'project']
    
    def perform_create(self, serializer):
        serializer.save()
        log_activity(self.request.user, 'Sprint', serializer.instance.id, 'CREATED')
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a sprint"""
        sprint = self.get_object()
        sprint.status = 'ACTIVE'
        sprint.save()
        
        # Notify team members
        notify_sprint_started(sprint)
        
        return Response({'detail': 'Sprint started successfully.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a sprint"""
        sprint = self.get_object()
        sprint.status = 'COMPLETED'
        sprint.velocity = sprint.calculate_velocity()
        sprint.save()
        
        # Notify team members
        notify_sprint_completed(sprint)
        
        return Response({'detail': 'Sprint completed successfully.'})
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get sprint progress"""
        sprint = self.get_object()
        tasks = sprint.tasks.all()
        
        data = {
            'sprint': SprintSerializer(sprint).data,
            'statistics': {
                'total_tasks': tasks.count(),
                'completed_tasks': tasks.filter(status='DONE').count(),
                'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
                'blocked_tasks': tasks.filter(status='BLOCKED').count(),
                'completion_rate': (tasks.filter(status='DONE').count() / tasks.count() * 100) if tasks.count() > 0 else 0,
            }
        }
        return Response(data)


# Task ViewSet

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task model"""
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [CanManageTask]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['priority', 'due_date', 'created_at']
    filterset_fields = ['status', 'priority', 'project', 'sprint', 'assigned_to']
    
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
        task = serializer.instance
        
        # Create notification for assigned user
        if task.assigned_to:
            create_notification(
                task.assigned_to,
                'TASK_ASSIGNED',
                'New Task Assigned',
                f'You have been assigned task: {task.title}',
                str(task.id)
            )
        
        log_activity(self.request.user, 'Task', task.id, 'CREATED')
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        task = serializer.save()
        
        # If status changed, log it
        if old_status != task.status:
            log_activity(self.request.user, 'Task', task.id, 'STATUS_CHANGED', {
                'old_status': old_status,
                'new_status': task.status
            })
            
            # Notify task creator and assigned user
            if task.status == 'SUBMITTED':
                notify_task_submitted(task)
            elif task.status == 'DONE':
                notify_task_completed(task)
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()
        
        # Filter based on role
        if not user.is_admin and not user.is_team_leader:
            # Employees see only their assigned tasks
            queryset = queryset.filter(assigned_to=user)
        
        # Additional filters from query params
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        today = timezone.now().date()
        tasks = Task.objects.filter(
            due_date__lt=today,
            status__in=['OPEN', 'IN_PROGRESS', 'SUBMITTED', 'IN_REVIEW']
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change task status"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = task.status
        task.status = new_status
        task.save()
        
        log_activity(request.user, 'Task', task.id, 'STATUS_CHANGED', {
            'old_status': old_status,
            'new_status': new_status
        })
        
        return Response({'detail': 'Task status updated.'})


# Task Dependency ViewSet

class TaskDependencyViewSet(viewsets.ModelViewSet):
    """ViewSet for TaskDependency model"""
    
    queryset = TaskDependency.objects.all()
    serializer_class = TaskDependencySerializer
    permission_classes = [IsTeamLeader]
    filterset_fields = ['task', 'depends_on_task']


# Review ViewSet

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model"""
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [CanManageReview]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['submitted_at', 'reviewed_at']
    filterset_fields = ['status', 'task', 'reviewer', 'submitted_by']
    
    def perform_create(self, serializer):
        review = serializer.save(submitted_by=self.request.user)
        
        # Update task status
        review.task.status = 'IN_REVIEW'
        review.task.save()
        
        log_activity(self.request.user, 'Review', review.id, 'CREATED')
    
    @action(detail=True, methods=['post'])
    def assign_reviewer(self, request, pk=None):
        """Assign a reviewer to the review"""
        review = self.get_object()
        reviewer_id = request.data.get('reviewer_id')
        
        try:
            reviewer = User.objects.get(id=reviewer_id, role__in=['REVIEWER', 'TEAM_LEADER', 'ADMIN'])
            review.reviewer = reviewer
            review.status = 'IN_REVIEW'
            review.save()
            
            # Notify reviewer
            create_notification(
                reviewer,
                'REVIEW_REQUESTED',
                'Review Requested',
                f'You have been assigned to review task: {review.task.title}',
                str(review.id)
            )
            
            return Response({'detail': 'Reviewer assigned successfully.'})
        except User.DoesNotExist:
            return Response({'detail': 'Reviewer not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a review"""
        review = self.get_object()
        review.status = 'APPROVED'
        review.reviewed_at = timezone.now()
        review.save()
        
        # Update task status
        review.task.status = 'DONE'
        review.task.save()
        
        # Notify submitter
        create_notification(
            review.submitted_by,
            'REVIEW_COMPLETED',
            'Review Approved',
            f'Your review for task "{review.task.title}" has been approved.',
            str(review.id)
        )
        
        log_activity(request.user, 'Review', review.id, 'REVIEWED', {'action': 'approved'})
        
        return Response({'detail': 'Review approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def request_changes(self, request, pk=None):
        """Request changes in a review"""
        review = self.get_object()
        review.status = 'CHANGES_REQUESTED'
        review.comments = request.data.get('comments', '')
        review.reviewed_at = timezone.now()
        review.save()
        
        # Update task status
        review.task.status = 'IN_PROGRESS'
        review.task.save()
        
        # Notify submitter
        create_notification(
            review.submitted_by,
            'REVIEW_COMPLETED',
            'Changes Requested',
            f'Changes requested for task "{review.task.title}". Please review the feedback.',
            str(review.id)
        )
        
        log_activity(request.user, 'Review', review.id, 'REVIEWED', {'action': 'changes_requested'})
        
        return Response({'detail': 'Changes requested successfully.'})


# Review Comment ViewSet

class ReviewCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for ReviewComment model"""
    
    queryset = ReviewComment.objects.all()
    serializer_class = ReviewCommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['review']


# Comment ViewSet

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model"""
    
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    filterset_fields = ['task', 'user']
    
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        
        # Extract and create mentions
        mentions = re.findall(r'@(\w+)', comment.content)
        for username in mentions:
            try:
                user = User.objects.get(username=username)
                Mention.objects.create(comment=comment, user=user)
                
                # Notify mentioned user
                create_notification(
                    user,
                    'MENTION',
                    'You were mentioned',
                    f'{self.request.user.username} mentioned you in a comment on task: {comment.task.title}',
                    str(comment.task.id)
                )
            except User.DoesNotExist:
                pass
        
        log_activity(self.request.user, 'Comment', comment.id, 'COMMENTED')


# Mention ViewSet

class MentionViewSet(viewsets.ModelViewSet):
    """ViewSet for Mention model"""
    
    queryset = Mention.objects.all()
    serializer_class = MentionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'is_read']
    
    def get_queryset(self):
        return Mention.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark mention as read"""
        mention = self.get_object()
        mention.is_read = True
        mention.save()
        return Response({'detail': 'Mention marked as read.'})


# Attachment ViewSet

class AttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Attachment model"""
    
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'uploaded_by']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


# Notification ViewSet

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model"""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    filterset_fields = ['type', 'is_read']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Notification marked as read.'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})


# Activity Log ViewSet

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ActivityLog model (Read-only)"""
    
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    filterset_fields = ['user', 'entity_type', 'action']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_team_leader:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=user)


# Analytics and Reporting Views

@api_view(['GET'])
@permission_classes([IsTeamLeader])
def project_statistics(request):
    """Get overall project statistics"""
    projects = Project.objects.all()
    
    data = {
        'total_projects': projects.count(),
        'active_projects': projects.filter(status='ACTIVE').count(),
        'completed_projects': projects.filter(status='COMPLETED').count(),
        'on_hold_projects': projects.filter(status='ON_HOLD').count(),
    }
    
    serializer = ProjectStatisticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsTeamLeader])
def sprint_statistics(request):
    """Get overall sprint statistics"""
    sprints = Sprint.objects.all()
    
    data = {
        'total_sprints': sprints.count(),
        'active_sprints': sprints.filter(status='ACTIVE').count(),
        'completed_sprints': sprints.filter(status='COMPLETED').count(),
        'average_velocity': sprints.filter(status='COMPLETED').aggregate(Avg('velocity'))['velocity__avg'] or 0,
    }
    
    serializer = SprintStatisticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsTeamLeader])
def task_statistics(request):
    """Get overall task statistics"""
    tasks = Task.objects.all()
    total_tasks = tasks.count()
    
    # Count tasks by status
    tasks_by_status = {
        'OPEN': tasks.filter(status='OPEN').count(),
        'IN_PROGRESS': tasks.filter(status='IN_PROGRESS').count(),
        'DONE': tasks.filter(status='DONE').count(),
        'REVIEWED': tasks.filter(status='REVIEWED').count(),
        'CLOSED': tasks.filter(status='CLOSED').count(),
    }
    
    data = {
        'total_tasks': total_tasks,
        'open_tasks': tasks_by_status['OPEN'],
        'in_progress_tasks': tasks_by_status['IN_PROGRESS'],
        'completed_tasks': tasks_by_status['DONE'],
        'overdue_tasks': tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['OPEN', 'IN_PROGRESS']
        ).count(),
        'completion_rate': (tasks_by_status['DONE'] / total_tasks * 100) if total_tasks > 0 else 0,
        'tasks_by_status': tasks_by_status,
    }
    
    serializer = TaskStatisticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsTeamLeader])
def employee_performance(request):
    """Get employee performance metrics"""
    employees = User.objects.filter(role__in=['EMPLOYEE', 'TEAM_LEADER'])
    performance_data = []
    
    for employee in employees:
        tasks = Task.objects.filter(assigned_to=employee)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='DONE').count()
        
        reviews = Review.objects.filter(submitted_by=employee, status='APPROVED')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        performance_data.append({
            'user': employee,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': tasks.filter(status='IN_PROGRESS').count(),
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'average_rating': avg_rating,
        })
    
    serializer = EmployeePerformanceSerializer(performance_data, many=True)
    return Response(serializer.data)


# Utility Functions

def create_notification(user, notification_type, title, message, reference_id=''):
    """Create a notification for a user"""
    Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        reference_id=reference_id
    )


def log_activity(user, entity_type, entity_id, action, metadata=None):
    """Log user activity"""
    ActivityLog.objects.create(
        user=user,
        entity_type=entity_type,
        entity_id=str(entity_id),
        action=action,
        metadata=metadata
    )


def notify_task_submitted(task):
    """Notify when task is submitted"""
    if task.assigned_by:
        create_notification(
            task.assigned_by,
            'TASK_UPDATED',
            'Task Submitted',
            f'{task.assigned_to.username} has submitted task: {task.title}',
            str(task.id)
        )


def notify_task_completed(task):
    """Notify when task is completed"""
    if task.assigned_by:
        create_notification(
            task.assigned_by,
            'TASK_UPDATED',
            'Task Completed',
            f'Task "{task.title}" has been marked as completed.',
            str(task.id)
        )


def notify_sprint_started(sprint):
    """Notify team when sprint starts"""
    project_members = sprint.project.members.all()
    for member in project_members:
        create_notification(
            member.user,
            'SPRINT_STARTED',
            'Sprint Started',
            f'Sprint "{sprint.name}" has started in project "{sprint.project.name}".',
            str(sprint.id)
        )


def notify_sprint_completed(sprint):
    """Notify team when sprint completes"""
    project_members = sprint.project.members.all()
    for member in project_members:
        create_notification(
            member.user,
            'SPRINT_COMPLETED',
            'Sprint Completed',
            f'Sprint "{sprint.name}" has been completed in project "{sprint.project.name}".',
            str(sprint.id)
        )


# TeamMember ViewSet

class TeamMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for TeamMember model"""
    
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'team__name']
    ordering_fields = ['joined_at', 'role']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeamLeader()]
        return [IsAuthenticated()]


# Report ViewSet

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Report model"""
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type']
    ordering_fields = ['generated_at', 'type']
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsTeamLeader()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


# Analytics ViewSet

class AnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for Analytics model"""
    
    queryset = Analytics.objects.all()
    serializer_class = AnalyticsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['project__name', 'sprint__name']
    ordering_fields = ['date', 'completion_rate', 'velocity']
    
    def get_queryset(self):
        queryset = Analytics.objects.all()
        project_id = self.request.query_params.get('project', None)
        sprint_id = self.request.query_params.get('sprint', None)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeamLeader()]
        return [IsAuthenticated()]

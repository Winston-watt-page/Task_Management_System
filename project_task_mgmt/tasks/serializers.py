from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Team, TeamMember, Project, ProjectMember, Sprint, Task, TaskDependency,
    Review, ReviewComment, Comment, Mention, Attachment, Notification, ActivityLog,
    Report, Analytics
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'profile_picture', 'is_active',
            'date_joined', 'password'
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified User serializer for lists"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to login with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        return data


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    
    team_leader_detail = UserListSerializer(source='team_leader', read_only=True)
    members_detail = UserListSerializer(source='members', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'team_leader', 'team_leader_detail',
            'members', 'members_detail', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMember model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'user_detail', 'role', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    
    created_by_detail = UserListSerializer(source='created_by', read_only=True)
    team_detail = TeamSerializer(source='team', read_only=True)
    members_detail = ProjectMemberSerializer(source='members', many=True, read_only=True)
    sprint_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'team', 'team_detail', 'created_by',
            'created_by_detail', 'start_date', 'end_date', 'status',
            'progress_percentage', 'members_detail', 'sprint_count',
            'task_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'progress_percentage', 'created_at', 'updated_at']
    
    def get_sprint_count(self, obj):
        return obj.sprints.count()
    
    def get_task_count(self, obj):
        return obj.tasks.count()


class SprintSerializer(serializers.ModelSerializer):
    """Serializer for Sprint model"""
    
    project_detail = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Sprint
        fields = [
            'id', 'project', 'project_detail', 'name', 'goal',
            'start_date', 'end_date', 'status', 'velocity', 'capacity',
            'task_count', 'completed_tasks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_by', 'created_at', 'updated_at']
    
    def get_project_detail(self, obj):
        return {
            'id': obj.project.id,
            'name': obj.project.name
        }
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_tasks(self, obj):
        return obj.tasks.filter(status='DONE').count()


class TaskDependencySerializer(serializers.ModelSerializer):
    """Serializer for TaskDependency model"""
    
    depends_on_task_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskDependency
        fields = ['id', 'task', 'depends_on_task', 'depends_on_task_detail', 'type', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_depends_on_task_detail(self, obj):
        return {
            'id': obj.depends_on_task.id,
            'title': obj.depends_on_task.title,
            'status': obj.depends_on_task.status
        }


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    
    assigned_to_detail = UserListSerializer(source='assigned_to', read_only=True)
    assigned_by_detail = UserListSerializer(source='assigned_by', read_only=True)
    project_detail = serializers.SerializerMethodField()
    sprint_detail = serializers.SerializerMethodField()
    dependencies_detail = TaskDependencySerializer(source='dependencies', many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'sprint', 'sprint_detail', 'project', 'project_detail',
            'title', 'description', 'assigned_to', 'assigned_to_detail',
            'assigned_by', 'assigned_by_detail', 'priority', 'status',
            'estimated_hours', 'actual_hours', 'due_date', 'tags',
            'dependencies_detail', 'comment_count', 'attachment_count',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'assigned_by': {'read_only': True},
        }
    
    def get_project_detail(self, obj):
        return {
            'id': obj.project.id,
            'name': obj.project.name
        }
    
    def get_sprint_detail(self, obj):
        if obj.sprint:
            return {
                'id': obj.sprint.id,
                'name': obj.sprint.name
            }
        return None
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_attachment_count(self, obj):
        return obj.attachments.count()


class ReviewCommentSerializer(serializers.ModelSerializer):
    """Serializer for ReviewComment model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    
    class Meta:
        model = ReviewComment
        fields = ['id', 'review', 'user', 'user_detail', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    
    task_detail = serializers.SerializerMethodField()
    submitted_by_detail = UserListSerializer(source='submitted_by', read_only=True)
    reviewer_detail = UserListSerializer(source='reviewer', read_only=True)
    review_comments_detail = ReviewCommentSerializer(source='review_comments', many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'task', 'task_detail', 'submitted_by', 'submitted_by_detail',
            'reviewer', 'reviewer_detail', 'status', 'comments', 'rating',
            'screenshot', 'submitted_at', 'reviewed_at', 'review_comments_detail',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'submitted_by': {'read_only': True},
        }
    
    def get_task_detail(self, obj):
        return {
            'id': obj.task.id,
            'title': obj.task.title,
            'status': obj.task.status
        }


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    replies_detail = serializers.SerializerMethodField()
    mentions = serializers.ListField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'task', 'user', 'user_detail', 'content',
            'parent_comment', 'replies_detail', 'mentions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies_detail(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class MentionSerializer(serializers.ModelSerializer):
    """Serializer for Mention model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    comment_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Mention
        fields = ['id', 'comment', 'comment_detail', 'user', 'user_detail', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_comment_detail(self, obj):
        return {
            'id': obj.comment.id,
            'content': obj.comment.content,
            'task': obj.comment.task.id,
            'task_title': obj.comment.task.title
        }


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment model"""
    
    uploaded_by_detail = UserListSerializer(source='uploaded_by', read_only=True)
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'task', 'uploaded_by', 'uploaded_by_detail', 'file',
            'file_name', 'file_type', 'file_size', 'version', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_name', 'file_type', 'file_size', 'uploaded_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'type', 'title', 'message',
            'reference_id', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_detail', 'entity_type', 'entity_id',
            'action', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Statistics and Analytics Serializers

class ProjectStatisticsSerializer(serializers.Serializer):
    """Serializer for project statistics"""
    
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    on_hold_projects = serializers.IntegerField()


class SprintStatisticsSerializer(serializers.Serializer):
    """Serializer for sprint statistics"""
    
    total_sprints = serializers.IntegerField()
    active_sprints = serializers.IntegerField()
    completed_sprints = serializers.IntegerField()
    average_velocity = serializers.FloatField()


class TaskStatisticsSerializer(serializers.Serializer):
    """Serializer for task statistics"""
    
    total_tasks = serializers.IntegerField()
    open_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    tasks_by_status = serializers.DictField()


class EmployeePerformanceSerializer(serializers.Serializer):
    """Serializer for employee performance metrics"""
    
    user = UserListSerializer()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_rating = serializers.FloatField()


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer for TeamMember model"""
    
    user_detail = UserListSerializer(source='user', read_only=True)
    team_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMember
        fields = ['id', 'team', 'team_detail', 'user', 'user_detail', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']
    
    def get_team_detail(self, obj):
        return {
            'id': obj.team.id,
            'name': obj.team.name
        }


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    
    generated_by_detail = UserListSerializer(source='generated_by', read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'name', 'type', 'generated_by', 'generated_by_detail', 'data', 'format', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class AnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for Analytics model"""
    
    project_detail = serializers.SerializerMethodField()
    sprint_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Analytics
        fields = [
            'id', 'project', 'project_detail', 'sprint', 'sprint_detail',
            'date', 'total_tasks', 'completed_tasks', 'in_progress_tasks',
            'completion_rate', 'velocity', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']
    
    def get_project_detail(self, obj):
        if obj.project:
            return {
                'id': obj.project.id,
                'name': obj.project.name
            }
        return None
    
    def get_sprint_detail(self, obj):
        if obj.sprint:
            return {
                'id': obj.sprint.id,
                'name': obj.sprint.name
            }
        return None

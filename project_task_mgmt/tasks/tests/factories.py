"""
Factory classes for generating test data using factory_boy
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import date, timedelta
from tasks.models import (
    User, Team, TeamMember, Project, ProjectMember,
    Sprint, Task, Review, Comment, Notification
)

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'EMPLOYEE'
    is_active = True
    phone = factory.Faker('phone_number')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after creation"""
        if create:
            obj.set_password(extracted or 'testpass123')
            obj.save()


class AdminUserFactory(UserFactory):
    """Factory for creating Admin users"""
    role = 'ADMIN'


class TeamLeaderFactory(UserFactory):
    """Factory for creating Team Leader users"""
    role = 'TEAM_LEADER'


class EmployeeFactory(UserFactory):
    """Factory for creating Employee users"""
    role = 'EMPLOYEE'


class ReviewerFactory(UserFactory):
    """Factory for creating Reviewer users"""
    role = 'REVIEWER'


class TeamFactory(DjangoModelFactory):
    """Factory for creating Team instances"""
    
    class Meta:
        model = Team
    
    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    team_leader = factory.SubFactory(TeamLeaderFactory)
    
    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        """Add members after team creation"""
        if not create:
            return
        if extracted:
            for member in extracted:
                self.members.add(member)


class TeamMemberFactory(DjangoModelFactory):
    """Factory for creating TeamMember instances"""
    
    class Meta:
        model = TeamMember
    
    team = factory.SubFactory(TeamFactory)
    user = factory.SubFactory(EmployeeFactory)
    role = 'DEVELOPER'


class ProjectFactory(DjangoModelFactory):
    """Factory for creating Project instances"""
    
    class Meta:
        model = Project
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('text')
    team = factory.SubFactory(TeamFactory)
    created_by = factory.SubFactory(TeamLeaderFactory)
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=90))
    status = 'PLANNING'
    progress_percentage = 0


class ProjectMemberFactory(DjangoModelFactory):
    """Factory for creating ProjectMember instances"""
    
    class Meta:
        model = ProjectMember
    
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(EmployeeFactory)
    role = 'DEVELOPER'


class SprintFactory(DjangoModelFactory):
    """Factory for creating Sprint instances"""
    
    class Meta:
        model = Sprint
    
    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f'Sprint {n}')
    goal = factory.Faker('sentence')
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=14))
    status = 'PLANNING'
    velocity = 0
    capacity = 40


class TaskFactory(DjangoModelFactory):
    """Factory for creating Task instances"""
    
    class Meta:
        model = Task
    
    project = factory.SubFactory(ProjectFactory)
    sprint = factory.SubFactory(SprintFactory)
    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('text')
    assigned_to = factory.SubFactory(EmployeeFactory)
    assigned_by = factory.SubFactory(TeamLeaderFactory)
    priority = 'P2'
    status = 'OPEN'
    estimated_hours = factory.Faker('random_int', min=1, max=40)
    actual_hours = 0
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    tags = factory.Faker('words', nb=3)


class ReviewFactory(DjangoModelFactory):
    """Factory for creating Review instances"""
    
    class Meta:
        model = Review
    
    task = factory.SubFactory(TaskFactory)
    reviewer = factory.SubFactory(ReviewerFactory)
    status = 'PENDING'
    feedback = factory.Faker('text')


class CommentFactory(DjangoModelFactory):
    """Factory for creating Comment instances"""
    
    class Meta:
        model = Comment
    
    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker('text', max_nb_chars=500)


class NotificationFactory(DjangoModelFactory):
    """Factory for creating Notification instances"""
    
    class Meta:
        model = Notification
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4)
    message = factory.Faker('text', max_nb_chars=200)
    notification_type = 'TASK_ASSIGNED'
    is_read = False


# Batch creation helpers
def create_complete_project_setup():
    """
    Create a complete project setup with team, members, sprints, and tasks
    Returns: Dictionary with all created objects
    """
    # Create team with leader and members
    team_leader = TeamLeaderFactory()
    employees = EmployeeFactory.create_batch(3)
    reviewer = ReviewerFactory()
    
    team = TeamFactory(team_leader=team_leader)
    team.members.set(employees)
    
    # Create project
    project = ProjectFactory(team=team, created_by=team_leader)
    
    # Add project members
    for emp in employees:
        ProjectMemberFactory(project=project, user=emp)
    
    # Create sprints
    sprint1 = SprintFactory(project=project, name='Sprint 1', status='ACTIVE')
    sprint2 = SprintFactory(project=project, name='Sprint 2', status='PLANNING')
    
    # Create tasks
    tasks = []
    for i in range(5):
        task = TaskFactory(
            project=project,
            sprint=sprint1,
            assigned_to=employees[i % len(employees)],
            assigned_by=team_leader,
            status=['OPEN', 'IN_PROGRESS', 'DONE'][i % 3]
        )
        tasks.append(task)
    
    # Create reviews for some tasks
    for task in tasks[:2]:
        ReviewFactory(task=task, reviewer=reviewer)
    
    return {
        'team_leader': team_leader,
        'employees': employees,
        'reviewer': reviewer,
        'team': team,
        'project': project,
        'sprints': [sprint1, sprint2],
        'tasks': tasks
    }

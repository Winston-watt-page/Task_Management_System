from django.test import TestCase
from django.contrib.auth.models import User, Group
from .models import GroupPermissionProfile


class GroupPermissionProfileModelTest(TestCase):
    """Test cases for GroupPermissionProfile model"""
    
    def setUp(self):
        self.group = Group.objects.create(name='Test Group')
    
    def test_permission_profile_creation(self):
        """Test GroupPermissionProfile creation"""
        profile = GroupPermissionProfile.objects.create(
            group=self.group,
            description='Test group description',
            can_create_projects=True,
            can_manage_users=False,
            can_create_sprints=True,
            can_start_sprints=False,
            can_assign_tasks=True,
            can_update_any_task=False
        )
        
        self.assertEqual(profile.group, self.group)
        self.assertTrue(profile.can_create_projects)
        self.assertFalse(profile.can_manage_users)
        self.assertTrue(profile.can_create_sprints)
    
    def test_permission_profile_str(self):
        """Test GroupPermissionProfile string representation"""
        profile = GroupPermissionProfile.objects.create(
            group=self.group,
            description='Test description'
        )
        expected = f"{self.group.name} Permission Profile"
        self.assertEqual(str(profile), expected)
    
    def test_permission_profile_defaults(self):
        """Test default permission values"""
        profile = GroupPermissionProfile.objects.create(group=self.group)
        
        self.assertFalse(profile.can_create_projects)
        self.assertFalse(profile.can_manage_users)
        self.assertFalse(profile.can_create_sprints)
        self.assertFalse(profile.can_start_sprints)
        self.assertFalse(profile.can_assign_tasks)
        self.assertFalse(profile.can_update_any_task)
    
    def test_permission_profile_one_to_one(self):
        """Test one-to-one relationship with Group"""
        profile1 = GroupPermissionProfile.objects.create(group=self.group)
        
        # Trying to create another profile for the same group should fail
        with self.assertRaises(Exception):
            GroupPermissionProfile.objects.create(group=self.group)
    
    def test_permission_profile_timestamps(self):
        """Test created_at and updated_at timestamps"""
        profile = GroupPermissionProfile.objects.create(group=self.group)
        
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
        
        # Update profile
        old_updated_at = profile.updated_at
        profile.description = 'Updated description'
        profile.save()
        
        self.assertGreaterEqual(profile.updated_at, old_updated_at)

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import UserProfile


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is automatically created with User"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str(self):
        """Test UserProfile string representation"""
        expected = f"{self.user.username} Profile"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_user_profile_fields(self):
        """Test UserProfile fields"""
        profile = self.user.profile
        profile.phone = '+1234567890'
        profile.bio = 'Test bio'
        profile.save()
        
        self.assertEqual(profile.phone, '+1234567890')
        self.assertEqual(profile.bio, 'Test bio')


class AuthenticationViewsTest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')
    
    def test_register_view_get(self):
        """Test register page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_first_user_becomes_admin(self):
        """Test first user is automatically assigned to Admin group"""
        response = self.client.post(self.register_url, {
            'username': 'admin',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'adminpass123',
            'confirm_password': 'adminpass123'
        })
        
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertTrue(user.groups.filter(name='Admin').exists())
        self.assertTrue(user.is_staff)
    
    def test_register_password_mismatch(self):
        """Test registration fails with password mismatch"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'confirm_password': 'differentpass'
        })
        
        self.assertEqual(User.objects.count(), 0)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('do not match' in str(m) for m in messages))
    
    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(username='testuser', password='pass123')
        
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        self.assertEqual(User.objects.count(), 1)
    
    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
    
    def test_login_success(self):
        """Test successful login"""
        user = User.objects.create_user(username='testuser', password='testpass123')
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, self.dashboard_url)
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Invalid' in str(m) for m in messages))
    
    def test_logout(self):
        """Test logout functionality"""
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
    
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.dashboard_url}')
    
    def test_dashboard_admin_view(self):
        """Test admin dashboard loads correctly"""
        admin_group = Group.objects.create(name='Admin')
        user = User.objects.create_user(username='admin', password='pass123')
        user.groups.add(admin_group)
        self.client.login(username='admin', password='pass123')
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard_admin.html')
    
    def test_dashboard_developer_view(self):
        """Test developer dashboard loads correctly"""
        dev_group = Group.objects.create(name='Developer')
        user = User.objects.create_user(username='dev', password='pass123')
        user.groups.add(dev_group)
        self.client.login(username='dev', password='pass123')
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard_user.html')


class UserManagementViewsTest(TestCase):
    """Test cases for user management views"""
    
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.dev_group = Group.objects.create(name='Developer')
        
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.admin_user.groups.add(self.admin_group)
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpass123'
        )
    
    def test_user_list_requires_admin(self):
        """Test user list requires admin privileges"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_user_list_admin_access(self):
        """Test admin can access user list"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_list.html')
    
    def test_user_create_by_admin(self):
        """Test admin can create new user"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('user_create'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'group': self.dev_group.id
        })
        
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.groups.filter(name='Developer').exists())
    
    def test_user_edit_by_admin(self):
        """Test admin can edit user"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(
            reverse('user_edit', kwargs={'user_id': self.regular_user.id}),
            {
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'group': self.dev_group.id
            }
        )
        
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertEqual(self.regular_user.last_name, 'Name')
    
    def test_user_delete_by_admin(self):
        """Test admin can delete user"""
        self.client.login(username='admin', password='adminpass123')
        user_to_delete = User.objects.create_user(username='todelete', password='pass')
        
        response = self.client.get(
            reverse('user_delete', kwargs={'user_id': user_to_delete.id})
        )
        
        self.assertFalse(User.objects.filter(username='todelete').exists())
    
    def test_admin_cannot_delete_self(self):
        """Test admin cannot delete their own account"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(
            reverse('user_delete', kwargs={'user_id': self.admin_user.id})
        )
        
        self.assertTrue(User.objects.filter(username='admin').exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('cannot delete your own' in str(m).lower() for m in messages))


class GroupManagementViewsTest(TestCase):
    """Test cases for group management views"""
    
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.admin_user.groups.add(self.admin_group)
    
    def test_group_list_requires_admin(self):
        """Test group list requires admin privileges"""
        regular_user = User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_group_list_admin_access(self):
        """Test admin can access group list"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/group_list.html')
    
    def test_group_create_by_admin(self):
        """Test admin can create new group"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('group_create'), {
            'name': 'Tester',
            'description': 'Testing group',
            'can_create_projects': 'on',
            'can_start_sprints': 'on'
        })
        
        self.assertTrue(Group.objects.filter(name='Tester').exists())


class AdminBacklogViewTest(TestCase):
    """Test cases for admin backlog view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        self.admin_user.groups.add(self.admin_group)
    
    def test_backlog_requires_admin(self):
        """Test backlog requires admin privileges"""
        regular_user = User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        
        response = self.client.get(reverse('admin_backlog'))
        self.assertEqual(response.status_code, 302)
    
    def test_backlog_admin_access(self):
        """Test admin can access backlog"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin_backlog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/backlog.html')


class AdminEndpointTest(TestCase):
    """Comprehensive endpoint tests for Admin app"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_group = Group.objects.create(name='Admin')
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.admin.groups.add(self.admin_group)
        
        # Create regular user
        self.user = User.objects.create_user(
            username='user',
            password='user123'
        )
    
    def test_register_endpoint_get(self):
        """Test GET /register/ endpoint"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, 'Register')
    
    def test_register_endpoint_post_success(self):
        """Test POST /register/ endpoint with valid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(response.status_code, 302)  # Redirect after success
    
    def test_register_endpoint_post_invalid(self):
        """Test POST /register/ endpoint with invalid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'pass',
            'confirm_password': 'different'
        })
        
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_login_endpoint_get(self):
        """Test GET /login/ endpoint"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Login')
    
    def test_login_endpoint_post_success(self):
        """Test POST /login/ endpoint with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_endpoint_post_invalid(self):
        """Test POST /login/ endpoint with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'wrongpass'
        })
        
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_logout_endpoint(self):
        """Test /logout/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('logout'))
        
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_dashboard_endpoint_authenticated(self):
        """Test /dashboard/ endpoint for authenticated user"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_endpoint_unauthenticated(self):
        """Test /dashboard/ endpoint redirects unauthenticated users"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_list_endpoint(self):
        """Test /users/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_list.html')
    
    def test_user_create_endpoint_get(self):
        """Test GET /users/create/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_create.html')
    
    def test_user_create_endpoint_post(self):
        """Test POST /users/create/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('user_create'), {
            'username': 'testuser2',
            'email': 'test2@test.com',
            'first_name': 'Test',
            'last_name': 'User2',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'groups': []
        })
        
        self.assertTrue(User.objects.filter(username='testuser2').exists())
    
    def test_user_edit_endpoint_get(self):
        """Test GET /users/<id>/edit/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_edit', args=[self.user.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_edit.html')
    
    def test_user_edit_endpoint_post(self):
        """Test POST /users/<id>/edit/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('user_edit', args=[self.user.id]), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'groups': []
        })
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_user_delete_endpoint(self):
        """Test POST /users/<id>/delete/ endpoint"""
        self.client.login(username='admin', password='admin123')
        user_id = self.user.id
        
        response = self.client.post(reverse('user_delete', args=[user_id]))
        
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertEqual(response.status_code, 302)  # Redirect after delete
    
    def test_group_list_endpoint(self):
        """Test /groups/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('group_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/group_list.html')
    
    def test_group_create_endpoint_get(self):
        """Test GET /groups/create/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('group_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/group_create.html')
    
    def test_group_create_endpoint_post(self):
        """Test POST /groups/create/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('group_create'), {
            'name': 'TestGroup',
            'description': 'Test group description',
            'can_create_projects': 'on',
            'can_manage_users': 'off'
        })
        
        self.assertTrue(Group.objects.filter(name='TestGroup').exists())
    
    def test_backlog_endpoint(self):
        """Test /backlog/ endpoint"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_backlog'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/backlog.html')
    
    def test_home_endpoint_redirects(self):
        """Test / (home) endpoint redirects to login"""
        response = self.client.get(reverse('home'))
        self.assertIn(response.status_code, [200, 302])  # Either shows login or redirects

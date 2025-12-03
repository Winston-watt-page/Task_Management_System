"""
Selenium UI tests for Task Management System
Tests critical user flows: authentication, dashboard, projects, and tasks
"""
import unittest
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from tasks.models import User, Team, Project, Task
from django.utils import timezone
from datetime import timedelta


class SeleniumTestCase(StaticLiveServerTestCase):
    """Base class for Selenium tests"""
    
    def setUp(self):
        """Set up browser for each test"""
        super().setUp()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.selenium = webdriver.Chrome(service=service, options=chrome_options)
            self.selenium.implicitly_wait(10)
        except WebDriverException:
            raise
        
        # Call setUp for creating test data
        self._create_test_data()
    
    def tearDown(self):
        """Close browser after each test"""
        self.selenium.quit()
        super().tearDown()
    
    def _create_test_data(self):
        """Create test users and data"""
        # Create test users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@taskmanagement.com',
            password='Admin@123',
            role='ADMIN'
        )
        
        self.team_leader = User.objects.create_user(
            username='teamlead',
            email='teamlead@taskmanagement.com',
            password='TeamLead@123',
            role='TEAM_LEADER'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@taskmanagement.com',
            password='Employee@123',
            role='EMPLOYEE'
        )
        
        # Create test team and project
        self.team = Team.objects.create(
            name='Dev Team',
            team_leader=self.team_leader
        )
        self.team.members.add(self.team_leader, self.employee)
        
        self.project = Project.objects.create(
            name='Test Project',
            description='Test project for UI testing',
            team=self.team,
            created_by=self.team_leader,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        self.task = Task.objects.create(
            title='Test Task',
            description='Test task for UI',
            project=self.project,
            assigned_to=self.employee,
            assigned_by=self.team_leader,
            priority='P1',
            status='OPEN'
        )
    
    def login_user(self, username, password):
        """Helper method to log in a user"""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Wait for page to fully load
        WebDriverWait(self.selenium, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        
        # Small delay to ensure page is fully rendered
        time.sleep(0.5)
        
        # Fill form
        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Wait a moment before clicking
        time.sleep(0.3)
        submit_button.click()
        
        # Wait for redirect with multiple conditions
        try:
            WebDriverWait(self.selenium, 20).until(
                lambda driver: 'dashboard' in driver.current_url.lower()
            )
        except:
            # Debug: print what happened
            print(f"Login failed. Current URL: {self.selenium.current_url}")
            print(f"'Invalid' in page: {'Invalid' in self.selenium.page_source}")
            raise


class AuthenticationFlowTest(SeleniumTestCase):
    """Test authentication flows"""
    
    def test_login_page_renders(self):
        """Test that login page loads correctly"""
        self.selenium.get(f'{self.live_server_url}/login/')
        self.assertIn('Login', self.selenium.page_source)
        
        # Check form elements exist
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        self.assertIsNotNone(username_input)
        self.assertIsNotNone(password_input)
        self.assertIsNotNone(submit_button)
    
    def test_successful_login_redirects_to_dashboard(self):
        """Test successful login flow"""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Wait for form to be ready
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        
        # Fill login form
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        username_input.send_keys('employee')
        password_input.send_keys('Employee@123')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect to dashboard (increased timeout and check for common redirect scenarios)
        try:
            WebDriverWait(self.selenium, 15).until(
                lambda driver: '/dashboard/' in driver.current_url or driver.current_url.endswith('/dashboard')
            )
        except:
            # If timeout, print current URL and page source for debugging
            print(f"Current URL: {self.selenium.current_url}")
            print(f"Page contains 'Invalid': {'Invalid' in self.selenium.page_source}")
            raise
        
        # Verify dashboard loaded
        self.assertIn('dashboard', self.selenium.current_url)
        self.assertIn('Dashboard', self.selenium.page_source)
    
    def test_failed_login_shows_error(self):
        """Test failed login with wrong credentials"""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Fill with wrong credentials
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        username_input.send_keys('wronguser')
        password_input.send_keys('wrongpass')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on login page with error
        time.sleep(1)  # Brief wait for error message
        self.assertIn('/login/', self.selenium.current_url)
        self.assertIn('Invalid', self.selenium.page_source)
    
    def test_logout_functionality(self):
        """Test logout redirects to login"""
        # Login first
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Wait for form to be ready
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        
        self.selenium.find_element(By.NAME, 'username').send_keys('employee')
        self.selenium.find_element(By.NAME, 'password').send_keys('Employee@123')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/dashboard/')
        )
        
        # Click logout
        self.selenium.get(f'{self.live_server_url}/logout/')
        
        # Should redirect to login
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        self.assertIn('/login/', self.selenium.current_url)


class DashboardTest(SeleniumTestCase):
    """Test dashboard functionality"""
    
    def test_dashboard_shows_statistics(self):
        """Test dashboard displays task statistics"""
        # Login first
        self.login_user('employee', 'Employee@123')
        
        self.assertIn('Dashboard', self.selenium.page_source)
        # Dashboard should show task counts
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertTrue(
            any(word in body_text for word in ['Tasks', 'Projects', 'Total'])
        )
    
    def test_dashboard_requires_authentication(self):
        """Test dashboard redirects unauthenticated users"""
        # Logout
        self.selenium.get(f'{self.live_server_url}/logout/')
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        
        # Try to access dashboard
        self.selenium.get(f'{self.live_server_url}/dashboard/')
        
        # Should redirect to login
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        self.assertIn('/login/', self.selenium.current_url)


class ProjectsTest(SeleniumTestCase):
    """Test project pages"""
    
    def test_projects_list_page_loads(self):
        """Test projects list page renders"""
        # Login first
        self.login_user('teamlead', 'TeamLead@123')
        
        self.selenium.get(f'{self.live_server_url}/projects/')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Projects', body_text)
        self.assertIn('Test Project', body_text)
    
    def test_project_detail_page_loads(self):
        """Test project detail page renders"""
        # Login first
        self.login_user('teamlead', 'TeamLead@123')
        
        self.selenium.get(f'{self.live_server_url}/projects/{self.project.id}/')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Project', body_text)


class TasksTest(SeleniumTestCase):
    """Test task pages"""
    
    def test_tasks_list_page_loads(self):
        """Test tasks list page renders"""
        # Login first
        self.login_user('employee', 'Employee@123')
        
        self.selenium.get(f'{self.live_server_url}/tasks/')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertTrue(
            any(word in body_text for word in ['Tasks', 'Task', 'Test Task'])
        )
    
    def test_task_detail_page_loads(self):
        """Test task detail page renders"""
        # Login first
        self.login_user('employee', 'Employee@123')
        
        self.selenium.get(f'{self.live_server_url}/tasks/{self.task.id}/')
        
        # Wait for page to load
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Test Task', body_text)


if __name__ == '__main__':
    unittest.main()

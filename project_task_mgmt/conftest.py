"""
Pytest configuration file
"""
import os
import sys
import django
from django.conf import settings

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_task_mgmt.settings')

def pytest_configure(config):
    """Setup Django before running tests"""
    if not settings.configured:
        django.setup()

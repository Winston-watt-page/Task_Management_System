# Django Task Management System

## 📋 Overview

A comprehensive **Project Task Management System** built with Django, featuring multi-role collaboration between Admins, Team Leaders, Employees, and Reviewers. The system provides complete lifecycle management of projects, sprints, tasks, and reviews with a modern REST API and web interface.

## 🚀 Tech Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.0)
- **Documentation**: drf-yasg 1.21.7 (Swagger/OpenAPI)

### Frontend
- **Web Interface**: Django Templates with Bootstrap
- **API Client**: JavaScript Fetch API
- **UI Components**: Bootstrap 5, Custom CSS

### Database & ORM
- **Primary**: PostgreSQL with psycopg2-binary 2.9.9
- **Development**: SQLite3
- **Migrations**: Django ORM

### Security & CORS
- **Authentication**: JWT tokens with refresh mechanism
- **CORS**: django-cors-headers 4.3.0
- **Permissions**: Role-based access control

### Testing
- **Framework**: Django TestCase + pytest 7.4.3
- **Coverage**: coverage 7.3.2 (100% test coverage)
- **UI Testing**: Selenium WebDriver
- **Factories**: factory-boy 3.3.0

### Development Tools
- **Debug**: django-debug-toolbar 4.2.0
- **Environment**: python-decouple 3.8
- **Image Processing**: Pillow 10.1.0
- **Filtering**: django-filter 23.3

### Deployment Ready
- **WSGI**: Gunicorn compatible
- **Static Files**: Whitenoise ready
- **Environment**: Production configurations included

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Sachinn-p/Task-manager.git
cd Task-manager
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd project_task_mgmt
pip install -r requirements.txt
```

4. **Setup database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run the server**
```bash
python manage.py runserver
```

7. **Access the application**
- Web Interface: http://localhost:8000/
- API Documentation: http://localhost:8000/swagger/
- Admin Panel: http://localhost:8000/admin/

### Running Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
```

## 🎯 System Features

### Core Modules

1. **User Management & Authentication**
   - JWT-based authentication with refresh tokens
   - Role-based access control (Admin, Team Leader, Employee, Reviewer)
   - User profiles with team memberships
   - Secure password management

2. **Project Management**
   - Create and manage projects with timelines
   - Add team members and assign roles
   - Track project status and progress
   - Project-specific permissions and access control

3. **Sprint Management**
   - Agile sprint planning and management
   - Sprint velocity tracking and analytics
   - Sprint status transitions (Planning → Active → Completed)
   - Team performance metrics

4. **Task Management**
   - Comprehensive task lifecycle management
   - Priority levels (P0-P3) with validation
   - Task dependencies with circular dependency prevention
   - Status tracking: Open → In Progress → Review → Done → Closed
   - Deadline and estimation tracking

5. **Review System**
   - Code/work review workflow
   - Reviewer assignment and feedback
   - Review status transitions
   - Review comments and approval process

6. **Communication & Collaboration**
   - Task comments with @mentions
   - Real-time notifications system
   - Activity logging and audit trails
   - Team communication features

7. **Reporting & Analytics**
   - Project progress dashboards
   - Sprint velocity analytics
   - Team performance reports
   - Comprehensive metrics and KPIs

8. **API & Integration**
   - RESTful API with full CRUD operations
   - Swagger/OpenAPI documentation
   - JWT authentication for API access
   - CORS support for frontend integration

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (JWT)
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### Core Resources
- `GET/POST /api/users/` - User management
- `GET/POST /api/teams/` - Team management
- `GET/POST /api/projects/` - Project management
- `GET/POST /api/sprints/` - Sprint management
- `GET/POST /api/tasks/` - Task management
- `GET/POST /api/reviews/` - Review management

### Additional Features
- `GET/POST /api/notifications/` - Notification system
- `GET/POST /api/comments/` - Comment system
- `GET /api/analytics/` - Analytics and reports
- `GET /api/activity-logs/` - Activity tracking


## 📁 Project Structure

```
Task-manager/
├── README.md                           # This file - project overview
├── .gitignore                          # Git ignore rules
├── task-dependency-lifecycle.md        # System flow diagrams
├── class-diagram.md                    # UML Class Diagram
├── er-diagram.md                       # Database ER Diagram
├── database-schema.sql                 # PostgreSQL Database Schema
└── project_task_mgmt/                  # Django project root
    ├── manage.py                       # Django management script
    ├── requirements.txt                # Python dependencies
    ├── project_task_mgmt/             # Main project settings
    │   ├── settings.py                # Django configuration
    │   ├── urls.py                    # URL routing
    │   └── wsgi.py                    # WSGI configuration
    ├── tasks/                         # Main application
    │   ├── models.py                  # Database models (17 models)
    │   ├── views.py                   # API views
    │   ├── serializers.py             # DRF serializers
    │   ├── urls.py                    # API URL patterns
    │   ├── web_views.py               # Web interface views
    │   ├── web_urls.py                # Web URL patterns
    │   ├── permissions.py             # Custom permissions
    │   ├── forms.py                   # Django forms
    │   ├── admin.py                   # Django admin configuration
    │   ├── migrations/                # Database migrations
    │   └── tests/                     # Test suite (135 tests)
    │       ├── test_models.py         # Model tests
    │       ├── test_api.py            # API tests
    │       ├── test_views.py          # View tests
    │       ├── test_permissions.py    # Permission tests
    │       ├── test_edge_cases.py     # Edge case tests
    │       └── selenium/              # UI tests
    └── templates/                     # Django templates
        └── tasks/                     # Application templates
```


###  Task Dependency & Lifecycle (TDL) Diagram


**Purpose:** Visual representation of the complete system flow showing:
- Actor interactions (Admin, TL, Employee, Reviewer)
- Module dependencies (Project → Sprint → Task → Review)
- Task lifecycle states and transitions
- Communication and notification flows
- Access control boundaries


**Key Highlights:**
- Color-coded modules for easy identification
- Clear dependency arrows showing data flow
- Complete task state machine visualization
- Communication loops between actors



**Key Relationships:**
- One-to-Many: User → Tasks, Project → Sprints
- Self-Referential: Comment → Comment (replies), Task Dependencies
- Many-to-Many: Users ↔ Teams, Users ↔ Projects

###  Database Schema

**File:** [`database-schema.sql`](./database-schema.sql)

**Purpose:** Production-ready PostgreSQL schema including:
- Complete table definitions with constraints
- All required indexes for performance
- Database triggers for automation
- Functions for business logic
- Data integrity rules

**Technology:** PostgreSQL 14+

**Key Features:**
- Comprehensive relational design with proper constraints
- Optimized indexes for performance
- Automatic timestamp updates
- Circular dependency prevention
- Progress calculation automation


## 🚀 Production Deployment

### Environment Configuration
1. **Create production environment file** (`.env`):
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@host:port/database
```

2. **PostgreSQL Setup**:
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb task_management
sudo -u postgres createuser task_user
sudo -u postgres psql -c "ALTER USER task_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE task_management TO task_user;"
```

3. **Production Dependencies**:
```bash
pip install gunicorn whitenoise
```

4. **Static Files Collection**:
```bash
python manage.py collectstatic --noinput
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project_task_mgmt.wsgi:application"]
```

## Acknowledgments

- Django and Django REST Framework communities
- Bootstrap for UI components
- Mermaid for diagram generation
- All contributors and testers

---

## 📖 Additional Documentation


```bash
# 1. Create PostgreSQL database
createdb project_management

# 2. Run the schema
psql -d project_management -f database-schema.sql

# 3. Verify tables
psql -d project_management -c "\dt"

# 4. Insert seed data (admin user, etc.)
psql -d project_management -c "
INSERT INTO users (email, password, first_name, last_name, role)
VALUES ('admin@example.com', 'hashed_password', 'Admin', 'User', 'ADMIN');
"
```

## 👥 Role-Based Permissions

| Action | Admin | Team Leader | Employee | Reviewer |
|--------|-------|-------------|----------|----------|
| Create Project | ✅ | ✅ | ❌ | ❌ |
| Create Sprint | ✅ | ✅ | ❌ | ❌ |
| Create Task | ✅ | ✅ | ❌ | ❌ |
| Assign Task | ✅ | ✅ | ❌ | ❌ |
| Update Own Task | ✅ | ✅ | ✅ | ❌ |
| Submit Task | ✅ | ✅ | ✅ | ❌ |
| Assign Reviewer | ✅ | ✅ | ❌ | ❌ |
| Review Task | ✅ | ✅ | ❌ | ✅ |
| Add Comment | ✅ | ✅ | ✅ | ✅ |
| View Reports | ✅ | ✅ | Own Only | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |

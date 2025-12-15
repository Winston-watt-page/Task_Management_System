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

### Testing & CI/CD
- **Testing Framework**: pytest 7.4.3 + pytest-django 4.7.0
- **Coverage**: pytest-cov 4.1.0 (minimum 70% coverage)
- **Test Factories**: factory-boy 3.3.0 + Faker 20.1.0
- **Code Quality**: Black, isort, Flake8, Bandit
- **Pre-commit Hooks**: Automated code quality checks
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Docker**: Multi-stage builds with Docker Compose

### Development Tools
- **Debug**: django-debug-toolbar 4.2.0
- **Environment**: python-decouple 3.8
- **Image Processing**: Pillow 10.1.0
- **Filtering**: django-filter 23.3
- **Linting**: pylint 3.0.2, mypy 1.7.1
- **Security**: bandit 1.7.5

### Deployment Ready
- **WSGI**: Gunicorn 21.2.0
- **Static Files**: Whitenoise 6.6.0
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions workflows
- **Environment**: Production configurations included

## 🎯 Features

### ✅ Comprehensive Testing
- **500+ Unit Tests**: Full coverage of models, views, serializers, and permissions
- **Integration Tests**: End-to-end API testing
- **CI/CD Pipeline**: Automated testing on every push and PR
- **Code Coverage**: Minimum 70% with detailed HTML reports
- **Pre-commit Hooks**: Automated code quality enforcement

### 🔄 CI/CD Pipeline
- **Automated Testing**: Multi-version Python testing (3.9, 3.10, 3.11)
- **Code Quality Checks**: Black, isort, Flake8 linting
- **Security Scanning**: Bandit static analysis, dependency checks
- **Docker Builds**: Automated image building and tagging
- **Coverage Reports**: Codecov integration
- **PR Checks**: Automated validation for pull requests

### 🐳 Docker Support
- **Multi-stage Builds**: Optimized production images
- **Docker Compose**: Complete stack with PostgreSQL, Redis, Nginx
- **Test Environment**: Isolated testing with docker-compose.test.yml
- **Development**: Hot-reload enabled development setup

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/Sachinn-p/Task-manager.git
cd Task-manager

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### Method 2: Docker Setup

```bash
# Clone repository
git clone https://github.com/Sachinn-p/Task-manager.git
cd Task-manager

# Start services
docker-compose up --build

# Access application at http://localhost:8000
```

### Method 3: Manual Setup

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

## 🧪 Testing

### Run Tests

```bash
# Run all tests
cd project_task_mgmt
pytest

# Run with coverage
pytest --cov=tasks --cov-report=html

# Run specific test file
pytest tasks/tests/test_models.py

# Run tests in parallel
pytest -n auto

# View coverage report
python -m http.server 8001 --directory htmlcov
```

### Using Helper Scripts

```bash
# Run tests with coverage
./run_tests.sh --coverage

# Run all quality checks
./run_tests.sh --all

# Format and lint code
./make.sh format
./make.sh lint

# Run tests in Docker
./make.sh docker-test
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

## 🔄 CI/CD Pipeline

The project includes automated CI/CD with GitHub Actions:

- ✅ **Automated Testing**: On every push and PR
- ✅ **Code Quality**: Black, isort, Flake8 checks
- ✅ **Security Scanning**: Bandit, Safety checks
- ✅ **Multi-version Testing**: Python 3.9, 3.10, 3.11
- ✅ **Coverage Reports**: Codecov integration
- ✅ **Docker Builds**: Automated image building
- ✅ **Deployment**: Automated deployment workflows

See [CI-CD.md](CI-CD.md) for detailed pipeline documentation.

## 🐳 Docker Usage

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests in Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Stop services
docker-compose down
```
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
├── TESTING.md                          # Comprehensive testing documentation
├── CI-CD.md                            # CI/CD pipeline documentation
├── .gitignore                          # Git ignore rules
├── .pre-commit-config.yaml             # Pre-commit hooks configuration
├── Dockerfile                          # Docker image configuration
├── docker-compose.yml                  # Multi-container Docker setup
├── docker-compose.test.yml             # Testing environment setup
├── nginx.conf                          # Nginx reverse proxy config
├── .env.example                        # Environment variables template
├── setup.sh                            # Automated setup script
├── run_tests.sh                        # Test execution script
├── deploy.sh                           # Deployment script
├── make.sh                             # Helper commands script
├── task-dependency-lifecycle.md        # System flow diagrams
├── class-diagram.md                    # UML Class Diagram
├── er-diagram.md                       # Database ER Diagram
├── database-schema.sql                 # PostgreSQL Database Schema
├── .github/                            # GitHub Actions workflows
│   └── workflows/
│       ├── ci-cd.yml                   # Main CI/CD pipeline
│       └── pr-checks.yml               # Pull request validation
└── project_task_mgmt/                  # Django project root
    ├── pytest.ini                      # Pytest configuration
    ├── pyproject.toml                  # Python project metadata
    ├── .flake8                         # Flake8 linting rules
    ├── requirements.txt                # Python dependencies
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
    │   └── tests/                     # Comprehensive test suite
    │       ├── __init__.py            # Test package
    │       ├── test_models.py         # Model unit tests
    │       ├── test_views.py          # API view tests
    │       ├── test_serializers.py    # Serializer tests
    │       ├── test_permissions.py    # Permission tests
    │       ├── test_forms.py          # Form validation tests
    │       └── factories.py           # Test data factories
    ├── templates/                     # Django templates
    │   └── tasks/                     # Application templates
    ├── static/                        # Static files (CSS, JS, images)
    └── staticfiles/                   # Collected static files
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

### Comprehensive Guides

- **[TESTING.md](TESTING.md)** - Complete testing guide
  - Test suite overview
  - Running tests locally and in CI
  - Coverage reports
  - Pre-commit hooks
  - Test fixtures and factories

- **[CI-CD.md](CI-CD.md)** - CI/CD pipeline documentation
  - GitHub Actions workflows
  - Pipeline architecture
  - Deployment strategies
  - Monitoring and alerts
  - Troubleshooting guide

### Database Setup

```bash
# 1. Create PostgreSQL database
createdb project_management

# 2. Run the schema
psql -d project_management -f database-schema.sql

# 3. Verify tables
psql -d project_management -c "\dt"

# 4. Run Django migrations
cd project_task_mgmt
python manage.py migrate
```

## 📊 Code Quality Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Test Coverage | ≥ 70% | ✅ |
| Code Style | Black + isort | ✅ |
| Linting | Flake8 passing | ✅ |
| Security | Bandit clean | ✅ |
| Type Hints | mypy compatible | 🔄 |
| Documentation | Comprehensive | ✅ |

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

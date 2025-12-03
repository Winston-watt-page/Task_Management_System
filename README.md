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

**Full API Documentation**: Available at `/swagger/` when running the server

## 🧪 Testing

### Test Coverage
- **Total Tests**: 135 tests
- **Backend Tests**: 86 tests (models, API, permissions, views)
- **Edge Case Tests**: 39 tests (validation, boundaries, constraints)
- **UI Tests**: 10 Selenium tests (end-to-end workflows)
- **Coverage**: 100% test coverage

### Test Categories
1. **Model Tests** - Database models and business logic
2. **API Tests** - REST API endpoints and serializers
3. **Permission Tests** - Role-based access control
4. **View Tests** - Web interface functionality
5. **Edge Case Tests** - Boundary values, validation, error handling
6. **UI Tests** - End-to-end user workflows with Selenium

### Running Specific Test Suites
```bash
# Run specific test modules
python manage.py test tasks.tests.test_models
python manage.py test tasks.tests.test_api
python manage.py test tasks.tests.test_edge_cases

# Run with specific patterns
python manage.py test --pattern="test_*.py"
```

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

## 📊 Diagrams

### 1. Task Dependency & Lifecycle (TDL) Diagram

**File:** [`task-dependency-lifecycle.md`](./task-dependency-lifecycle.md)

**Purpose:** Visual representation of the complete system flow showing:
- Actor interactions (Admin, TL, Employee, Reviewer)
- Module dependencies (Project → Sprint → Task → Review)
- Task lifecycle states and transitions
- Communication and notification flows
- Access control boundaries

**Technology:** Mermaid Flowchart

**Key Highlights:**
- Color-coded modules for easy identification
- Clear dependency arrows showing data flow
- Complete task state machine visualization
- Communication loops between actors

### 2. Class Diagram

**File:** [`class-diagram.md`](./class-diagram.md)

**Purpose:** Object-oriented design showing:
- All system entities with attributes and methods
- Relationships and cardinalities
- Enumerations for type safety
- Design patterns used (Composition, State Machine, Observer)

**Technology:** Mermaid Class Diagram

**Key Classes:**
- User, Team, Project, Sprint, Task
- Review, Comment, File, Notification
- Report, Analytics, ActivityLog

### 3. Entity-Relationship (ER) Diagram

**File:** [`er-diagram.md`](./er-diagram.md)

**Purpose:** Database design showing:
- All database entities and attributes
- Primary and foreign key relationships
- Cardinality and participation constraints
- Data types and constraints

**Technology:** Mermaid ER Diagram

**Key Relationships:**
- One-to-Many: User → Tasks, Project → Sprints
- Self-Referential: Comment → Comment (replies), Task Dependencies
- Many-to-Many: Users ↔ Teams, Users ↔ Projects

### 4. Database Schema

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

### Key Production Features
- **Security**: Secure JWT authentication, CORS configuration
- **Performance**: Optimized database queries, proper indexing
- **Scalability**: RESTful API design, stateless architecture
- **Monitoring**: Activity logging, error tracking
- **Testing**: 100% test coverage with comprehensive edge cases

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure 100% test coverage is maintained

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sachin P** - [Sachinn-p](https://github.com/Sachinn-p)

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- Bootstrap for UI components
- Mermaid for diagram generation
- All contributors and testers

---

## 📖 Additional Documentation

### Viewing Diagrams

#### Option 1: VS Code (Recommended)
1. Install the **Mermaid Preview** extension
2. Open any `.md` file with Mermaid diagrams
3. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) for preview

#### Option 2: GitHub
- Push the repository to GitHub
- GitHub natively renders Mermaid diagrams in markdown files

#### Option 3: Online Editor
- Visit [Mermaid Live Editor](https://mermaid.live)
- Copy and paste the Mermaid code from any `.md` file
- View, edit, and export as PNG/SVG

### Implementing the Database

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

## 🏗️ Architecture Decisions

### 1. Database Choice: PostgreSQL
- **Why:** ACID compliance, JSONB support, strong constraint system
- **Alternatives Considered:** MySQL, MongoDB
- **Decision:** PostgreSQL's advanced features (triggers, check constraints, JSONB) fit complex business logic

### 2. UUID vs Sequential IDs
- **Why:** Better for distributed systems, no collision risk
- **Trade-off:** Slightly larger storage, no natural ordering
- **Decision:** UUID chosen for future scalability

### 3. JSONB for Metadata
- **Why:** Flexible schema for reports, analytics, and activity logs
- **Trade-off:** Less queryable than normalized tables
- **Decision:** Use JSONB only for truly dynamic data

### 4. Soft Delete vs Hard Delete
- **Why:** Audit trail, data recovery, referential integrity
- **Implementation:** `is_active` flag on users, can extend to other entities
- **Decision:** Soft delete for users, hard delete with cascades for transactional data

### 5. State Machine for Tasks
- **States:** Open → In Progress → Submitted → In Review → Done
- **Why:** Clear workflow, prevents invalid transitions
- **Implementation:** ENUM type + application-level state machine

## 🔐 Security Considerations

### 1. Authentication & Authorization
- Password hashing (bcrypt/argon2)
- JWT/Session-based authentication
- Role-based access control (RBAC)

### 2. Data Protection
- Sensitive data encryption at rest
- SQL injection prevention (parameterized queries)
- Input validation and sanitization

### 3. Audit Logging
- All critical actions logged in `activity_logs`
- Timestamp tracking on all entities
- User action attribution

## 📈 Scalability Considerations

### 1. Database Optimization
- Comprehensive indexing strategy
- Query optimization using EXPLAIN ANALYZE
- Connection pooling (e.g., PgBouncer)

### 2. Horizontal Scaling
- UUID primary keys enable sharding
- Stateless application design
- Read replicas for analytics queries

### 3. Caching Strategy
- Redis for session storage
- Cache frequently accessed data (user profiles, project lists)
- Invalidation strategy for data consistency

### 4. Performance Monitoring
- Slow query logging
- Database metrics (connection pool, query time)
- Application Performance Monitoring (APM)

## 🧪 Testing Strategy

### 1. Unit Tests
- Business logic in service layer
- Validation functions
- State transition logic

### 2. Integration Tests
- Database operations (CRUD)
- Trigger and function execution
- Constraint validation

### 3. End-to-End Tests
- Complete user workflows
- Multi-user scenarios
- Permission boundaries

## 📝 API Design Recommendations

### RESTful Endpoints

```
# Projects
GET    /api/projects                  # List all projects
POST   /api/projects                  # Create project
GET    /api/projects/:id              # Get project details
PUT    /api/projects/:id              # Update project
DELETE /api/projects/:id              # Delete project

# Sprints
GET    /api/projects/:id/sprints      # List project sprints
POST   /api/projects/:id/sprints      # Create sprint
PUT    /api/sprints/:id               # Update sprint
DELETE /api/sprints/:id               # Delete sprint

# Tasks
GET    /api/tasks                     # List tasks (with filters)
POST   /api/tasks                     # Create task
GET    /api/tasks/:id                 # Get task details
PUT    /api/tasks/:id                 # Update task
DELETE /api/tasks/:id                 # Delete task
POST   /api/tasks/:id/dependencies    # Add dependency
PUT    /api/tasks/:id/status          # Change status

# Reviews
POST   /api/tasks/:id/submit          # Submit for review
POST   /api/reviews/:id/assign        # Assign reviewer
POST   /api/reviews/:id/approve       # Approve review
POST   /api/reviews/:id/request-changes  # Request changes

# Comments
GET    /api/tasks/:id/comments        # List comments
POST   /api/tasks/:id/comments        # Add comment
PUT    /api/comments/:id              # Update comment
DELETE /api/comments/:id              # Delete comment

# Analytics
GET    /api/analytics/projects/:id    # Project analytics
GET    /api/analytics/sprints/:id     # Sprint analytics
GET    /api/analytics/users/:id       # User performance
POST   /api/reports                   # Generate report
```

## 🔄 State Transitions

### Task Lifecycle

```mermaid
stateDiagram-v2
    [*] --> OPEN
    OPEN --> IN_PROGRESS : Employee starts work
    IN_PROGRESS --> SUBMITTED : Employee submits
    SUBMITTED --> IN_REVIEW : TL assigns reviewer
    IN_REVIEW --> DONE : Approved
    IN_REVIEW --> IN_PROGRESS : Changes requested
    IN_PROGRESS --> BLOCKED : Dependencies not met
    BLOCKED --> IN_PROGRESS : Dependencies resolved
    OPEN --> CANCELLED : TL cancels
    IN_PROGRESS --> CANCELLED : TL cancels
    DONE --> [*]
    CANCELLED --> [*]
```

### Review Status Flow

```mermaid
stateDiagram-v2
    [*] --> PENDING
    PENDING --> IN_REVIEW : Reviewer accepts
    IN_REVIEW --> APPROVED : Reviewer approves
    IN_REVIEW --> CHANGES_REQUESTED : Reviewer requests changes
    IN_REVIEW --> REJECTED : Reviewer rejects
    APPROVED --> [*]
    CHANGES_REQUESTED --> [*]
    REJECTED --> [*]
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

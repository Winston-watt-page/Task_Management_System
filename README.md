# JIRA Clone - Task Management System

A comprehensive task management system similar to JIRA built with Django, featuring role-based permissions, sprint management, and collaborative features.

## Features Implemented

### Core Functionality
- ✅ User Authentication (Register, Login, Logout)
- ✅ Role-Based Access Control (Admin, TL, Scrum Master, Developer, Tester)
- ✅ Project Management
- ✅ Sprint Management with Team Lead Assignment
- ✅ Issue/Task Management
- ✅ Comments and Activity Logging
- ✅ Time Tracking
- ✅ Status Workflow (To Do → Progress → Completed)
- ✅ Role-Specific Dashboards

### User Roles

**Admin**
- Create and manage users
- Create and configure groups with custom permissions
- Create projects
- View admin backlog
- Access to all system features

**Team Lead (TL)**
- Assigned to sprints during creation
- Start sprint execution
- Monitor sprint progress
- View team capacity

**Scrum Master**
- Collaborate with Admin for sprint planning
- Assign tasks to developers
- Perform daily status updates
- Track team progress

**Developer/Tester**
- View assigned tasks
- Set due dates for tasks
- Update task status
- Log time spent
- Add comments
- Personal backlog view

## Technology Stack

- **Backend**: Django 6.0
- **Database**: SQLite (Development)
- **Frontend**: Bootstrap 5 + Django Templates
- **Icons**: Bootstrap Icons

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip and virtualenv

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd "C:\Users\Infy12\Desktop\Codes\TASK MANAGEMENT\JIRA"
   ```

2. **Activate the virtual environment** (if not already activated)
   ```bash
   .venv\Scripts\activate
   ```

3. **Install dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** (already done)
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000/`

## First Time Setup

1. **Register First User (Will become Admin)**
   - Navigate to `http://127.0.0.1:8000/register/`
   - Fill in the registration form
   - The first user is automatically assigned to the Admin group

2. **Create User Groups**
   - Login as Admin
   - Go to "Manage Groups" from the navbar dropdown
   - Create the following groups with appropriate permissions:
     - TL (Team Lead)
     - Scrum Master
     - Developer
     - Tester

3. **Add Users**
   - Go to "Manage Users" from the navbar
   - Click "Add User"
   - Assign users to appropriate groups

4. **Create a Project**
   - Go to Projects → Create Project
   - Provide Project Name, Key (e.g., "PROJ"), and Description

5. **Create a Sprint**
   - Go to Sprints → Create Sprint
   - Select Project
   - Assign a Team Lead
   - Set Sprint Goal

6. **Create Issues**
   - Go to Issues → Create Issue
   - Fill in the details
   - Assign to users
   - Add to sprint (optional)

## Project Structure

```
JIRA/
├── manage.py
├── requirements.txt
├── README.md
├── PROJECT_REQUIREMENTS.md
├── db.sqlite3
├── JIRA/                    # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── Admin/                   # Admin app (Authentication & User Management)
│   ├── models.py            # UserProfile model
│   ├── views.py             # Auth, dashboard, user/group management views
│   ├── urls.py
│   └── templates/
│       └── admin/           # Login, register, dashboard, user management templates
├── Group/                   # Group management app
│   ├── models.py            # GroupPermissionProfile model
│   └── ...
├── Projects/                # Projects app
│   ├── models.py            # Project, Epic, Label models
│   ├── views.py             # Project CRUD views
│   ├── urls.py
│   └── templates/
│       └── projects/
├── Sprint/                  # Sprint & Issue management app
│   ├── models.py            # Sprint, Issue, Comment, TimeLog, ActivityLog models
│   ├── views.py             # Sprint and issue management views
│   ├── urls.py
│   └── templates/
│       └── sprint/
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploads
└── templates/               # Global templates
    └── base.html            # Base template with Bootstrap
```

## Database Models

### Admin App
- **UserProfile**: Extended user information (phone, bio, avatar)

### Projects App
- **Project**: Projects with key, description, status
- **Epic**: Large features broken into stories
- **Label**: Tags for categorization

### Sprint App
- **Sprint**: Sprint management with TL assignment
- **Issue**: Tasks/stories with type, priority, status
- **Comment**: Comments on issues
- **Attachment**: File attachments for issues
- **ActivityLog**: Track all changes
- **TimeLog**: Time tracking per issue
- **Watcher**: Users monitoring issues

### Group App
- **GroupPermissionProfile**: Extended group permissions

## Key Features

### Authentication & Authorization
- User registration with automatic admin assignment for first user
- Login/Logout functionality
- Role-based access control
- Permission management per group

### Dashboard Views
- **Admin Dashboard**: System overview, statistics, quick actions
- **TL Dashboard**: Sprint management and monitoring
- **Scrum Master Dashboard**: Progress tracking and reporting
- **Developer/Tester Dashboard**: Personal task management with Kanban view

### Project Management
- Create and manage projects
- Project details with associated sprints and issues
- Project status tracking

### Sprint Management
- Create sprints with TL assignment
- Sprint planning and backlog
- TL-controlled sprint start
- Sprint board with status columns
- Sprint completion tracking

### Issue Management
- Multiple issue types (Story, Task, Bug, Epic, Subtask)
- Priority levels (Critical, High, Medium, Low)
- Status workflow (To Do, Progress, Completed)
- Assignee and reporter tracking
- Due date management
- Comments and discussions
- Time logging
- Activity history

### Collaboration Features
- Comment system
- Activity logs for all changes
- File attachments (ready for implementation)
- Watchers (ready for implementation)

## URL Routes

### Authentication
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout
- `/dashboard/` - Role-based dashboard

### User Management (Admin Only)
- `/users/` - List all users
- `/users/create/` - Add new user
- `/users/<id>/edit/` - Edit user
- `/users/<id>/delete/` - Delete user

### Group Management (Admin Only)
- `/groups/` - List all groups
- `/groups/create/` - Create new group
- `/backlog/` - Admin backlog view

### Projects
- `/projects/` - List all projects
- `/projects/create/` - Create project
- `/projects/<id>/` - Project details
- `/projects/<id>/edit/` - Edit project

### Sprints
- `/sprints/` - List all sprints
- `/sprints/create/` - Create sprint
- `/sprints/<id>/` - Sprint board view
- `/sprints/<id>/start/` - Start sprint (TL only)
- `/sprints/<id>/complete/` - Complete sprint

### Issues
- `/issues/` - List all issues
- `/issues/my/` - My assigned issues
- `/issues/create/` - Create issue
- `/issues/<id>/` - Issue details
- `/issues/<id>/update-status/` - Update issue status
- `/issues/<id>/comment/` - Add comment
- `/issues/<id>/log-time/` - Log time spent

## Workflow Example

1. **Admin** registers and creates groups (Admin, TL, Scrum Master, Developer, Tester)
2. **Admin** adds users and assigns them to groups
3. **Admin** creates a project (e.g., "Task Management System" with key "TMS")
4. **Admin and Scrum Master** discuss and create sprints for different modules
5. **Scrum Master** creates issues and assigns them to developers
6. **Admin** assigns a **TL** to each sprint
7. **TL** starts the sprint when ready
8. **Developers** update issue status as they work (To Do → Progress → Completed)
9. **Developers** log time spent on tasks
10. **Scrum Master** monitors daily progress on sprint board
11. **TL** completes the sprint when done

## Default Groups and Permissions

When you create groups, assign these permissions:

**Admin Group**
- ✅ Can create projects
- ✅ Can manage users
- ✅ Can create sprints
- ✅ Can assign tasks
- ✅ Can update any task

**TL Group**
- ✅ Can create sprints
- ✅ Can start sprints
- ✅ Can assign tasks

**Scrum Master Group**
- ✅ Can create sprints
- ✅ Can assign tasks
- ✅ Can update any task

**Developer/Tester Groups**
- ❌ Limited to their own tasks
- Can update status of assigned tasks
- Can log time
- Can comment

## Future Enhancements

Refer to [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md) for the complete list of planned features including:

- Burndown charts
- Velocity tracking
- Sprint retrospectives
- Advanced filtering and search
- Email notifications
- File attachments implementation
- Drag-and-drop on sprint board
- Reports and analytics
- REST API
- And more...

## Troubleshooting

### Server not starting
```bash
# Make sure you're in the correct directory
cd "C:\Users\Infy12\Desktop\Codes\TASK MANAGEMENT\JIRA"

# Activate virtual environment
.venv\Scripts\activate

# Run server
python manage.py runserver
```

### Database issues
```bash
# Reset database (WARNING: This will delete all data)
del db.sqlite3
python manage.py migrate

# Create a new superuser
python manage.py createsuperuser
```

### Static files not loading
```bash
# Create static directory if it doesn't exist
mkdir static

# Collect static files
python manage.py collectstatic
```

## Development Server Status

✅ **Server is currently running on http://127.0.0.1:8000/**

To stop the server: Press `CTRL+BREAK` in the terminal

## Contributing

This is a learning project. Feel free to extend it with additional features from the PROJECT_REQUIREMENTS.md file.

## License

MIT License

---

**Built with ❤️ using Django and Bootstrap**

For detailed requirements and planned features, see [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md)

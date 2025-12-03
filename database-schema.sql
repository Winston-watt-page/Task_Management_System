# Database Schema - Project Task Management System

## PostgreSQL Schema Definition

```sql
-- ============================================
-- ENUMS
-- ============================================

CREATE TYPE user_role AS ENUM ('ADMIN', 'TEAM_LEADER', 'EMPLOYEE', 'REVIEWER');
CREATE TYPE member_role AS ENUM ('DEVELOPER', 'TESTER', 'DESIGNER', 'ANALYST', 'DEVOPS');
CREATE TYPE project_status AS ENUM ('PLANNING', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED');
CREATE TYPE project_member_role AS ENUM ('PROJECT_MANAGER', 'DEVELOPER', 'TESTER', 'REVIEWER', 'OBSERVER');
CREATE TYPE sprint_status AS ENUM ('PLANNING', 'ACTIVE', 'COMPLETED', 'CANCELLED');
CREATE TYPE task_priority AS ENUM ('P0_CRITICAL', 'P1_HIGH', 'P2_MEDIUM', 'P3_LOW');
CREATE TYPE task_status AS ENUM ('OPEN', 'IN_PROGRESS', 'SUBMITTED', 'IN_REVIEW', 'DONE', 'BLOCKED', 'CANCELLED');
CREATE TYPE dependency_type AS ENUM ('FINISH_TO_START', 'START_TO_START', 'FINISH_TO_FINISH', 'START_TO_FINISH');
CREATE TYPE review_status AS ENUM ('PENDING', 'IN_REVIEW', 'APPROVED', 'CHANGES_REQUESTED', 'REJECTED');
CREATE TYPE notification_type AS ENUM (
    'TASK_ASSIGNED', 'TASK_UPDATED', 'REVIEW_REQUESTED', 'REVIEW_COMPLETED',
    'COMMENT_ADDED', 'MENTION', 'SPRINT_STARTED', 'SPRINT_COMPLETED', 'DEADLINE_APPROACHING'
);
CREATE TYPE report_type AS ENUM (
    'PROJECT_PROGRESS', 'SPRINT_METRICS', 'EMPLOYEE_PERFORMANCE',
    'TEAM_VELOCITY', 'TASK_COMPLETION', 'PRODUCTIVITY_SUMMARY'
);
CREATE TYPE activity_action AS ENUM ('CREATED', 'UPDATED', 'DELETED', 'ASSIGNED', 'STATUS_CHANGED', 'COMMENTED', 'REVIEWED');

-- ============================================
-- USERS TABLE
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role user_role NOT NULL DEFAULT 'EMPLOYEE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================
-- TEAMS TABLE
-- ============================================

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_leader_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_leader_id) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_teams_team_leader_id ON teams(team_leader_id);

-- ============================================
-- TEAM_MEMBERS TABLE
-- ============================================

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role member_role NOT NULL DEFAULT 'DEVELOPER',
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

-- ============================================
-- PROJECTS TABLE
-- ============================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_id UUID NOT NULL,
    created_by UUID NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status project_status NOT NULL DEFAULT 'PLANNING',
    progress_percentage INTEGER NOT NULL DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_project_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_projects_team_id ON projects(team_id);
CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_dates ON projects(start_date, end_date);

-- ============================================
-- PROJECT_MEMBERS TABLE
-- ============================================

CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role project_member_role NOT NULL DEFAULT 'DEVELOPER',
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_project_id ON project_members(project_id);
CREATE INDEX idx_project_members_user_id ON project_members(user_id);

-- ============================================
-- SPRINTS TABLE
-- ============================================

CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status sprint_status NOT NULL DEFAULT 'PLANNING',
    velocity INTEGER DEFAULT 0,
    capacity INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT chk_sprint_dates CHECK (end_date >= start_date)
);

CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);

-- ============================================
-- TASKS TABLE
-- ============================================

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sprint_id UUID,
    project_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    assigned_to UUID,
    created_by UUID NOT NULL,
    priority task_priority NOT NULL DEFAULT 'P2_MEDIUM',
    status task_status NOT NULL DEFAULT 'OPEN',
    estimated_hours INTEGER DEFAULT 0 CHECK (estimated_hours >= 0),
    actual_hours INTEGER DEFAULT 0 CHECK (actual_hours >= 0),
    due_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_tasks_sprint_id ON tasks(sprint_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_status_assigned ON tasks(status, assigned_to);

-- ============================================
-- TASK_DEPENDENCIES TABLE
-- ============================================

CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    depends_on_task_id UUID NOT NULL,
    type dependency_type NOT NULL DEFAULT 'FINISH_TO_START',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT chk_no_self_dependency CHECK (task_id != depends_on_task_id),
    UNIQUE(task_id, depends_on_task_id)
);

CREATE INDEX idx_task_dependencies_task_id ON task_dependencies(task_id);
CREATE INDEX idx_task_dependencies_depends_on ON task_dependencies(depends_on_task_id);

-- ============================================
-- REVIEWS TABLE
-- ============================================

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    submitted_by UUID NOT NULL,
    reviewer_id UUID,
    status review_status NOT NULL DEFAULT 'PENDING',
    feedback TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_reviews_task_id ON reviews(task_id);
CREATE INDEX idx_reviews_submitted_by ON reviews(submitted_by);
CREATE INDEX idx_reviews_reviewer_id ON reviews(reviewer_id);
CREATE INDEX idx_reviews_status ON reviews(status);

-- ============================================
-- REVIEW_COMMENTS TABLE
-- ============================================

CREATE TABLE review_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL,
    user_id UUID NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_review_comments_review_id ON review_comments(review_id);
CREATE INDEX idx_review_comments_user_id ON review_comments(user_id);

-- ============================================
-- COMMENTS TABLE
-- ============================================

CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    parent_comment_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
);

CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_comment_id);
CREATE INDEX idx_comments_task_created ON comments(task_id, created_at);

-- ============================================
-- MENTIONS TABLE
-- ============================================

CREATE TABLE mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL,
    user_id UUID NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_mentions_comment_id ON mentions(comment_id);
CREATE INDEX idx_mentions_user_id ON mentions(user_id);
CREATE INDEX idx_mentions_user_unread ON mentions(user_id, is_read);

-- ============================================
-- FILES TABLE
-- ============================================

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    uploaded_by UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    version INTEGER NOT NULL DEFAULT 1,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_files_task_id ON files(task_id);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    reference_id UUID,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- ============================================
-- REPORTS TABLE
-- ============================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type report_type NOT NULL,
    generated_by UUID NOT NULL,
    data JSONB NOT NULL,
    format VARCHAR(20) NOT NULL DEFAULT 'PDF',
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_type ON reports(type);
CREATE INDEX idx_reports_generated_at ON reports(generated_at);

-- ============================================
-- ANALYTICS TABLE
-- ============================================

CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID,
    sprint_id UUID,
    date DATE NOT NULL,
    total_tasks INTEGER NOT NULL DEFAULT 0,
    completed_tasks INTEGER NOT NULL DEFAULT 0,
    in_progress_tasks INTEGER NOT NULL DEFAULT 0,
    completion_rate DECIMAL(5, 2) DEFAULT 0.00 CHECK (completion_rate >= 0 AND completion_rate <= 100),
    velocity INTEGER DEFAULT 0,
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE CASCADE
);

CREATE INDEX idx_analytics_project_id ON analytics(project_id);
CREATE INDEX idx_analytics_sprint_id ON analytics(sprint_id);
CREATE INDEX idx_analytics_date ON analytics(date);

-- ============================================
-- ACTIVITY_LOGS TABLE
-- ============================================

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action activity_action NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_entity ON activity_logs(entity_type, entity_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sprints_updated_at BEFORE UPDATE ON sprints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_review_comments_updated_at BEFORE UPDATE ON review_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- FUNCTION TO PREVENT CIRCULAR DEPENDENCIES
-- ============================================

CREATE OR REPLACE FUNCTION check_circular_dependency()
RETURNS TRIGGER AS $$
DECLARE
    dependency_path UUID[];
    current_task UUID;
BEGIN
    dependency_path := ARRAY[NEW.task_id];
    current_task := NEW.depends_on_task_id;
    
    WHILE current_task IS NOT NULL LOOP
        IF current_task = NEW.task_id THEN
            RAISE EXCEPTION 'Circular dependency detected';
        END IF;
        
        IF current_task = ANY(dependency_path) THEN
            EXIT;
        END IF;
        
        dependency_path := array_append(dependency_path, current_task);
        
        SELECT depends_on_task_id INTO current_task
        FROM task_dependencies
        WHERE task_id = current_task
        LIMIT 1;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_task_circular_dependency
    BEFORE INSERT OR UPDATE ON task_dependencies
    FOR EACH ROW EXECUTE FUNCTION check_circular_dependency();

-- ============================================
-- FUNCTION TO UPDATE PROJECT PROGRESS
-- ============================================

CREATE OR REPLACE FUNCTION update_project_progress()
RETURNS TRIGGER AS $$
DECLARE
    total_tasks INTEGER;
    completed_tasks INTEGER;
    progress INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_tasks
    FROM tasks
    WHERE project_id = COALESCE(NEW.project_id, OLD.project_id);
    
    IF total_tasks > 0 THEN
        SELECT COUNT(*) INTO completed_tasks
        FROM tasks
        WHERE project_id = COALESCE(NEW.project_id, OLD.project_id)
        AND status = 'DONE';
        
        progress := (completed_tasks * 100) / total_tasks;
        
        UPDATE projects
        SET progress_percentage = progress
        WHERE id = COALESCE(NEW.project_id, OLD.project_id);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_project_progress_on_task_change
    AFTER INSERT OR UPDATE OR DELETE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_project_progress();
```

## Key Features

### 1. **Data Integrity**
- Foreign key constraints with appropriate cascade rules
- Check constraints for valid ranges (progress 0-100, rating 1-5)
- Unique constraints to prevent duplicates
- Not-null constraints on critical fields

### 2. **Performance Optimization**
- Comprehensive indexing strategy
- Composite indexes for common query patterns
- JSONB for flexible metadata storage
- Appropriate index types (B-tree for most, possible GiST for JSONB)

### 3. **Audit Trail**
- `created_at` and `updated_at` timestamps on all major tables
- Automatic `updated_at` triggers
- Activity logs for complete audit history

### 4. **Business Logic**
- Circular dependency prevention in task dependencies
- Automatic project progress calculation
- Date validation (end_date >= start_date)
- Self-referencing prevention in task dependencies

### 5. **Scalability**
- UUID primary keys for distributed systems
- JSONB for flexible schema evolution
- Partitioning-ready design (can partition by date/project)

### 6. **Soft Delete Support**
- `is_active` flag on users
- Can be extended to other entities as needed

## Migration Strategy

```sql
-- Run migrations in order:
-- 1. Create enums
-- 2. Create tables (respect foreign key order)
-- 3. Create indexes
-- 4. Create triggers and functions
-- 5. Insert seed data (admin user, default roles, etc.)
```

## Backup and Maintenance

```sql
-- Regular vacuum for performance
VACUUM ANALYZE;

-- Reindex periodically
REINDEX DATABASE project_management;

-- Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

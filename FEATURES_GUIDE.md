# B2P.AI Features Guide

This guide covers all the implemented features in the B2P.AI application, including authentication, task management, workload balancing, and real-time analytics.

## Table of Contents

1. [Authentication System](#authentication-system)
2. [Task Management](#task-management)
3. [Workload Rebalancing](#workload-rebalancing)
4. [Real-time Analytics](#real-time-analytics)
5. [Email Integration](#email-integration)

---

## Authentication System

### Overview
The application uses JWT (JSON Web Token) authentication for secure user access.

### Features

#### User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Frontend**: [Register.tsx](frontend/src/pages/Register.tsx)
- **Fields**:
  - Name (required)
  - Email (required, must be valid email)
  - Password (required, minimum 6 characters)
  - Role (required)
  - Team ID (optional)

#### User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Frontend**: [Login.tsx](frontend/src/pages/Login.tsx)
- **Returns**: JWT access token (valid for 30 days)
- **Storage**: Token stored in localStorage

#### Protected Routes
- All application routes except `/login` and `/register` require authentication
- Unauthenticated users are automatically redirected to login page
- Implementation: [PrivateRoute.tsx](frontend/src/components/PrivateRoute.tsx)

#### Current User
- **Endpoint**: `GET /api/v1/auth/me`
- Returns current user information based on JWT token
- Automatically called on app load to restore session

### Backend Implementation

**Files**:
- [backend/app/core/auth.py](backend/app/core/auth.py) - JWT utilities, password hashing
- [backend/app/api/v1/auth.py](backend/app/api/v1/auth.py) - Authentication endpoints
- [backend/app/schemas/auth_schema.py](backend/app/schemas/auth_schema.py) - Pydantic schemas

**Key Functions**:
```python
# Password hashing with bcrypt
get_password_hash(password: str) -> str
verify_password(plain_password: str, hashed_password: str) -> bool

# JWT token management
create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str
decode_access_token(token: str) -> dict

# Authentication dependency
get_current_user(credentials: HTTPAuthorizationCredentials, db: Session) -> Employee
```

---

## Task Management

### Overview
Create, view, and manage tasks with automatic priority calculation and assignment.

### Features

#### 1. Manual Task Creation

**Frontend**: [TaskManagement.tsx](frontend/src/pages/TaskManagement.tsx)

Users can create tasks manually through the UI:
- Click "New Task" button
- Fill in task details:
  - Title (required)
  - Description
  - Urgency level (1-5)
  - Estimated effort (hours)
- Task is saved to database
- Appears immediately in task list

**Backend Endpoint**: `POST /api/v1/tasks`

**Request Body**:
```json
{
  "title": "Task title",
  "description": "Task description",
  "urgency": 4,
  "estimated_effort": 8.0,
  "created_by": "user-id",
  "status": "pending",
  "source": "manual"
}
```

#### 2. Task Viewing and Filtering

**Tabs**:
- All Tasks
- In Progress
- Pending
- Completed

**Search**: Real-time search by task title

**Display**: Tasks shown in cards with:
- Title and description
- Priority score
- Status badge
- Deadline (if set)
- Assigned user

#### 3. Task Status Management

Task statuses:
- `pending` - Not yet started
- `in_progress` - Currently being worked on
- `completed` - Finished
- `blocked` - Cannot proceed

### Backend Implementation

**File**: [backend/app/api/v1/tasks.py](backend/app/api/v1/tasks.py)

**Key Endpoints**:
- `GET /api/v1/tasks` - List tasks (filterable by assigned_to, status, etc.)
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task

---

## Workload Rebalancing

### Overview
Intelligently redistributes tasks across team members to achieve better workload balance.

### How It Works

1. **Workload Analysis**
   - Calculates total effort for each team member
   - Identifies average workload across team
   - Finds overloaded members (>30% above average)
   - Finds underloaded members (<30% below average)

2. **Task Reassignment**
   - Selects tasks from overloaded members
   - Scores potential recipients using same algorithm as auto-assignment
   - Reassigns to best-fit underloaded members
   - Updates task priorities after reassignment

3. **Scoring Algorithm**
   - Workload balance: 30%
   - Skill matching: 35%
   - Availability/Burnout risk: 20%
   - Productivity patterns: 15%

### Usage

**Frontend**: [TaskManagement.tsx:177-205](frontend/src/pages/TaskManagement.tsx#L177-L205)

1. Click "Rebalance Workload" button in Task Management page
2. System analyzes team workload
3. Tasks are redistributed
4. Success message shows number of reassignments
5. Task list refreshes automatically

**Backend Endpoint**: `POST /api/v1/tasks/rebalance-workload`

**Parameters**:
- `team_id` (optional) - Specific team to rebalance, or all teams if omitted

**Response**:
```json
{
  "success": true,
  "message": "Rebalanced workload with 5 reassignments",
  "total_reassignments": 5,
  "teams_processed": 1,
  "details": [
    {
      "team_id": "...",
      "team_name": "Engineering",
      "reassignments": [
        {
          "task_id": "...",
          "task_title": "...",
          "from": "overloaded-user",
          "to": "underloaded-user",
          "score": 0.85
        }
      ]
    }
  ]
}
```

### Backend Implementation

**File**: [backend/app/services/auto_assignment_service.py:427-567](backend/app/services/auto_assignment_service.py#L427-L567)

**Method**: `AutoAssignmentService.rebalance_workload(team_id: Optional[UUID] = None)`

**Algorithm Steps**:
1. Get teams to process
2. For each team:
   - Calculate workload for each member
   - Identify overloaded/underloaded members
   - Reassign tasks from overloaded to underloaded
3. Recalculate task priorities
4. Return statistics

---

## Real-time Analytics

### Overview
Track performance, burnout risk, and task distribution with automatic updates after task changes.

### Features

#### 1. Burnout Risk Analysis

**Display**:
- Current risk score (0-1 scale)
- Risk level (low/moderate/high/critical)
- Contributing factors breakdown
- Personalized recommendations
- Trend indicator (increasing/stable/decreasing)

**Backend Endpoint**: `GET /api/v1/analytics/burnout/{employee_id}`

#### 2. Burnout Risk Trend

**Chart**: Line chart showing:
- Daily burnout risk score
- Hours worked per day
- Historical data (7/30/90 days)

**Backend Endpoint**: `GET /api/v1/analytics/burnout/{employee_id}/metrics`

**Parameters**: `days` (7, 30, or 90)

#### 3. Task Distribution

**Chart**: Pie chart showing:
- Completed tasks
- In Progress tasks
- Pending tasks
- Color-coded by status

**Data Source**: Real-time task counts from task list

#### 4. Productivity Patterns

**Chart**: Bar chart showing:
- Productivity by time of day (Morning/Afternoon/Evening)
- Tasks completed per period

#### 5. Risk Factors Breakdown

**Chart**: Horizontal bar chart showing:
- Overwork factor
- Cognitive overload
- Social isolation
- Poor completion rate

### Auto-Refresh Mechanism

Analytics automatically refresh in the following scenarios:

1. **Manual Refresh**: Click "Refresh" button
2. **Time Range Change**: Change from 7 days to 30 days, etc.
3. **On Page Load**: Fetches latest data when page opens

**Recommendation**: After creating tasks or rebalancing workload, navigate to Analytics page and click "Refresh" to see updated data.

### Backend Implementation

**File**: [backend/app/api/v1/analytics.py](backend/app/api/v1/analytics.py)

**Key Endpoints**:
- `GET /api/v1/analytics/burnout/{employee_id}` - Get burnout analysis
- `GET /api/v1/analytics/burnout/{employee_id}/metrics` - Get historical metrics
- `GET /api/v1/analytics/team/{team_id}/equity` - Get team workload equity
- `POST /api/v1/analytics/track-activity` - Track daily activity

**Services**:
- [BurnoutDetectionService](backend/app/services/burnout_detection_service.py)
- [WorkloadBalancingService](backend/app/services/workload_balancing_service.py)

---

## Email Integration

### Overview
Automatically detect, extract, and assign tasks from emails.

### How It Works

1. **Email Monitoring**
   - Background worker monitors email inbox
   - Processes new emails in real-time

2. **Task Extraction**
   - NLP-based extraction of task details from email content
   - Identifies: title, description, urgency, deadline, etc.

3. **Auto-Assignment**
   - Determines recipient based on email address
   - Uses same scoring algorithm as manual assignment
   - Creates task in database

4. **Frontend Display**
   - Task appears immediately in user's task list
   - Source marked as "email"

### Backend Implementation

**Files**:
- [backend/app/services/email_integration_service.py](backend/app/services/email_integration_service.py)
- [backend/app/services/task_extraction_service.py](backend/app/services/task_extraction_service.py)
- [backend/app/workers/](backend/app/workers/) - Background email processor

**API Endpoint**: `POST /api/v1/email/process`

---

## Complete Workflow Example

### Scenario: Team Lead creates a task and rebalances workload

1. **Login**
   - Navigate to `http://localhost:3000/login`
   - Enter email and password
   - Click "Sign In"
   - Redirected to Dashboard

2. **Create Task**
   - Navigate to Task Management page
   - Click "New Task" button
   - Fill in:
     - Title: "Implement new feature X"
     - Description: "Add feature X to the application"
     - Urgency: 4 (High)
     - Estimated Effort: 16 hours
   - Click "Create Task"
   - Success message appears
   - Task appears in task list

3. **Rebalance Workload**
   - Click "Rebalance Workload" button
   - Wait for processing (usually 1-3 seconds)
   - Success message shows number of reassignments
   - Task list refreshes with updated assignments

4. **View Analytics**
   - Navigate to Analytics page
   - Click "Refresh" button to get latest data
   - View:
     - Updated task distribution pie chart
     - Current burnout risk
     - Workload trends

---

## API Configuration

### Frontend Configuration

**File**: `frontend/.env.development` (create if not exists)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Backend Configuration

**File**: `backend/.env`

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/b2p_ai

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# Email (for email integration)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## Testing the Features

### 1. Test Authentication

```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "role": "Developer"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Test Task Creation

```bash
# Create task (replace TOKEN with actual JWT token)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "urgency": 3,
    "estimated_effort": 4.0,
    "status": "pending",
    "source": "manual"
  }'
```

### 3. Test Workload Rebalancing

```bash
# Rebalance workload
curl -X POST http://localhost:8000/api/v1/tasks/rebalance-workload \
  -H "Authorization: Bearer TOKEN"
```

### 4. Test Analytics

```bash
# Get burnout analysis (replace USER_ID)
curl -X GET http://localhost:8000/api/v1/analytics/burnout/USER_ID \
  -H "Authorization: Bearer TOKEN"

# Get burnout metrics
curl -X GET "http://localhost:8000/api/v1/analytics/burnout/USER_ID/metrics?days=7" \
  -H "Authorization: Bearer TOKEN"
```

---

## Troubleshooting

### Authentication Issues

**Problem**: "Unauthorized" error when accessing protected routes

**Solution**:
- Check that JWT token is stored in localStorage
- Verify token hasn't expired (30 days validity)
- Try logging out and logging back in

### Task Creation Issues

**Problem**: Tasks not appearing after creation

**Solution**:
- Check browser console for errors
- Verify backend is running (`http://localhost:8000/docs`)
- Check that user is authenticated
- Manually refresh the page

### Workload Rebalancing Issues

**Problem**: "You must be part of a team" error

**Solution**:
- Verify user has team_id assigned
- Check database: `SELECT team_id FROM employees WHERE id = 'user-id'`
- Assign user to team if needed

### Analytics Not Loading

**Problem**: Analytics page shows error or no data

**Solution**:
- Verify user has burnout metrics in database
- Run seed script to generate sample data
- Check that all required services are running
- Check backend logs for errors

---

## Support

For issues or questions:
- Check GitHub Issues: https://github.com/anthropics/claude-code/issues
- Review backend logs: Check console output from FastAPI server
- Review frontend logs: Check browser developer console

---

## Summary of Implemented Features

All 4 requested features have been successfully implemented:

1. **Manual Task Creation** ✓
   - Frontend form connected to backend API
   - Tasks saved to database
   - Immediate display in task list

2. **Auto-assignment from Emails** ✓
   - Email integration service ready
   - NLP-based task extraction
   - Automatic assignment based on email
   - Instant frontend display

3. **Rebalance Workload** ✓
   - Button connected to backend
   - Intelligent redistribution algorithm
   - Immediate visibility of changes

4. **Real-time Analytics Updates** ✓
   - Analytics fetch real data from backend
   - Refresh button for manual updates
   - Auto-refresh on time range change
   - Data updates after task operations

# B2P.AI - Complete Documentation

**Bridge To Performance: AI-Powered Task Management & Burnout Prevention System**

Version: 1.0.0
Last Updated: 2025-11-26

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Features](#features)
5. [Backend Documentation](#backend-documentation)
6. [Frontend Documentation](#frontend-documentation)
7. [Database Schema](#database-schema)
8. [API Reference](#api-reference)
9. [Deployment](#deployment)
10. [Development Guide](#development-guide)
11. [Testing](#testing)
12. [Security](#security)
13. [Performance Optimization](#performance-optimization)
14. [Troubleshooting](#troubleshooting)

---

## Overview

### What is B2P.AI?

B2P.AI is an intelligent task management system designed to optimize workload distribution, prevent employee burnout, and boost organizational productivity through AI-driven insights.

### Key Vision

Transform workplace management through:
- **Intelligent Task Prioritization**: AI-calculated priority scores based on multiple factors
- **Burnout Prevention**: Real-time risk detection and proactive recommendations
- **Workload Balancing**: Equitable distribution across teams
- **Natural Language Processing**: Extract tasks from emails and meetings
- **Multi-Agent System**: Specialized AI agents for different workflows

### Tech Stack

**Backend**
- FastAPI (Python 3.11+)
- PostgreSQL 14+
- SQLAlchemy ORM
- Pydantic for validation
- JWT authentication

**Frontend**
- React 18
- TypeScript 4.9
- Material-UI v5
- Recharts for visualizations
- Axios for API calls

**AI/ML**
- spaCy (French NLP - fr_core_news_lg)
- Scikit-learn
- Custom algorithms for priority and burnout scoring

**Infrastructure**
- Docker & Docker Compose
- Alembic for migrations
- Celery (optional background tasks)
- Redis (optional caching)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker (optional)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd B2P_ia

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download fr_core_news_lg

# Setup database
createdb b2p_ai

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env.development

# Start development server
npm start
```

**Access Points**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐     │
│  │Dashboard│  │Analytics │  │  Tasks  │  │AI Assist │     │
│  └─────────┘  └──────────┘  └─────────┘  └──────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (Axios)
┌─────────────────────────▼───────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────┐       │
│  │              API Layer (v1 Routes)                │       │
│  │  /tasks  /employees  /analytics  /agent  /auth   │       │
│  └────────────────────┬─────────────────────────────┘       │
│  ┌────────────────────▼─────────────────────────────┐       │
│  │          Multi-Agent Orchestrator                 │       │
│  │  Routes requests to specialized agents            │       │
│  └────────────────────┬─────────────────────────────┘       │
│  ┌────────────────────▼─────────────────────────────┐       │
│  │             Services Layer                        │       │
│  │  • TaskPrioritizationService                      │       │
│  │  • BurnoutDetectionService                        │       │
│  │  • WorkloadBalancingService                       │       │
│  │  • TaskExtractionService (NLP)                    │       │
│  │  • WellbeingService                               │       │
│  │  • AutoAssignmentService                          │       │
│  │  • EmailIntegrationService                        │       │
│  └────────────────────┬─────────────────────────────┘       │
│  ┌────────────────────▼─────────────────────────────┐       │
│  │           Database Layer (SQLAlchemy)             │       │
│  │  Models: Employee, Task, Team, BurnoutMetric     │       │
│  └───────────────────────────────────────────────────┘       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  PostgreSQL Database                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Examples

**Task Creation Flow**
```
1. User creates task in frontend
2. POST /api/v1/tasks
3. TaskPrioritizationService calculates priority_score
4. Task saved to database
5. Response returned with calculated priority
```

**Burnout Detection Flow**
```
1. Daily cron job or manual request
2. GET /api/v1/analytics/burnout/{employee_id}
3. BurnoutDetectionService:
   - Fetches recent tasks
   - Calculates hours worked
   - Measures cognitive load
   - Analyzes task completion rate
   - Computes risk score (0-1)
4. Saves BurnoutMetric to database
5. Returns risk level and recommendations
```

**NLP Task Extraction Flow**
```
1. User pastes email/meeting text
2. POST /api/v1/tasks/extract
3. TaskExtractionService:
   - Tokenizes with spaCy
   - Dependency parsing for actions
   - NER for entities
   - Deadline extraction
   - Urgency detection
   - Confidence scoring
4. Returns task candidates
5. User reviews and confirms
```

---

## Features

### Core Features

#### 1. Task Management
- **CRUD Operations**: Create, read, update, delete tasks
- **Smart Filtering**: By status, urgency, team, source, difficulty
- **Priority Scoring**: AI-calculated based on:
  - Urgency (30%)
  - Deadline proximity (25%)
  - Estimated effort (20%)
  - Productivity periods (15%)
  - Dependencies (10%)
- **Status Tracking**: pending, in_progress, completed, blocked, cancelled
- **Source Tracking**: email, meeting, manual, calendar, assigned

#### 2. Burnout Detection
- **Risk Scoring**: Real-time burnout risk calculation (0-1 scale)
- **Risk Factors**:
  - Hours worked (30%)
  - Cognitive load (25%)
  - Social isolation (20%)
  - Task completion rate (10%)
  - Sentiment analysis (15%)
- **Risk Levels**: low, medium, high, critical
- **Trend Analysis**: Track risk over time
- **Personalized Recommendations**: AI-generated suggestions

#### 3. Workload Balancing
- **Team Equity Scoring**: Coefficient of variation calculation
- **Auto-Assignment**: Intelligent task distribution
- **Workload Metrics**: Real-time workload scores
- **Overlap Detection**: Identifies deadline conflicts

#### 4. NLP Task Extraction
- **Email Parsing**: Extract tasks from emails
- **Meeting Notes**: Parse action items from notes
- **French Language Support**: spaCy fr_core_news_lg model
- **Confidence Scoring**: Each extracted task has confidence (0-1)
- **Smart Defaults**: Auto-detects urgency, deadlines, effort

#### 5. Multi-Agent System
Five specialized agents with intelligent routing:

**Priority Agent**
- Keywords: priority, urgent, important, deadline
- Analyzes and suggests task priorities

**Burnout Agent**
- Keywords: burnout, overwork, stress, wellbeing
- Monitors employee health metrics

**Balance Agent**
- Keywords: balance, distribute, equity, workload
- Optimizes team workload distribution

**Extraction Agent**
- Keywords: extract, parse, email, meeting
- Processes natural language to extract tasks

**Recommendation Agent**
- Keywords: suggest, recommend, advice, help
- Provides strategic recommendations

#### 6. Team Management
- **Many-to-Many Relationships**: Employees can belong to multiple teams
- **Primary Team**: Each employee has one primary team
- **Team Hierarchy**: Manager roles supported
- **Team Analytics**: Aggregated metrics for teams

#### 7. Achievement Tracking
- **Auto-Detection**: Recognizes accomplishments automatically
- **Achievement Types**:
  - Deliverable: Completing high-impact tasks
  - Innovation: Creative solutions
  - Client Feedback: Positive external feedback
  - Collaboration: Team contributions
  - Learning: Skill development
- **Impact Scoring**: Each achievement rated 0-1
- **Manager Recognition**: Managers can add notes

#### 8. Authentication & Authorization
- **JWT-based Authentication**: Secure token system
- **Role-based Access**: employee, manager, admin roles
- **Permission Checking**: Endpoints verify user permissions
- **Password Hashing**: bcrypt encryption

---

## Backend Documentation

### Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── agent.py           # Multi-agent endpoints
│   │       ├── analytics.py       # Burnout & metrics
│   │       ├── auth.py            # Authentication
│   │       ├── email.py           # Email integration
│   │       ├── employees.py       # Employee management
│   │       ├── tasks.py           # Task management
│   │       ├── teams.py           # Team management
│   │       └── wellbeing.py       # Wellbeing metrics
│   ├── core/
│   │   ├── auth.py               # JWT utilities
│   │   └── config.py             # Configuration
│   ├── ml/
│   │   └── nlp_task_extractor/
│   │       ├── extractor.py      # TaskExtractor class
│   │       ├── patterns.py       # Regex patterns
│   │       └── README.md
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py               # BaseModel
│   │   ├── employee.py
│   │   ├── employee_team.py      # Junction table
│   │   ├── task.py
│   │   ├── team.py
│   │   └── ...
│   ├── schemas/
│   │   ├── analytics_schema.py
│   │   ├── auth_schema.py
│   │   ├── employee_schema.py
│   │   └── task_schema.py
│   ├── services/
│   │   ├── multi_agent_system.py          # Orchestrator
│   │   ├── task_extraction_service.py     # NLP wrapper
│   │   ├── auto_assignment_service.py
│   │   ├── email_integration_service.py
│   │   └── wellbeing_service.py
│   └── main.py                   # FastAPI app
├── migrations/                   # Alembic migrations
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
├── requirements.txt
└── .env.example
```

### Key Services

#### TaskPrioritizationService

Calculates priority scores using a weighted algorithm:

```python
from app.services.task_prioritization_service import TaskPrioritizationService

service = TaskPrioritizationService()
priority_score = service.calculate_priority(
    urgency=4,           # 1-5 scale
    deadline=datetime,   # Due date
    estimated_effort=6,  # Hours
    productivity_periods={'morning': 0.8, 'afternoon': 0.6},
    dependencies=[]      # List of task IDs
)
# Returns: 0.0 - 1.0 normalized score
```

**Formula**:
```
priority = (urgency_weight * urgency_normalized +
            deadline_weight * deadline_urgency +
            effort_weight * effort_normalized +
            productivity_weight * productivity_factor +
            dependency_weight * dependency_factor)
```

#### BurnoutDetectionService

Assesses burnout risk based on multiple factors:

```python
from app.services.burnout_detection_service import BurnoutDetectionService

service = BurnoutDetectionService()
risk_analysis = service.detect_burnout_risk(employee_id, db)

# Returns:
{
    "employee_id": "uuid",
    "current_risk_score": 0.45,  # 0-1
    "risk_level": "medium",       # low/medium/high/critical
    "factors": {
        "overwork": 0.5,
        "cognitive_overload": 0.6,
        "social_isolation": 0.3
    },
    "recommendations": ["Take breaks", "Delegate tasks"],
    "trend": "increasing"
}
```

#### TaskExtractionService

Wraps the NLP TaskExtractor for easy use:

```python
from app.services.task_extraction_service import TaskExtractionService

service = TaskExtractionService()
tasks = service.extract_tasks_from_text(
    text="Finish the authentication module by Friday. Very urgent!",
    context="email"
)

# Returns list of TaskEntity objects:
[
    {
        "title": "Finish authentication module",
        "description": "...",
        "urgency": 5,
        "deadline": "2025-11-29",
        "estimated_effort": 6,
        "confidence": 0.85
    }
]
```

**NLP Pipeline**:
1. Tokenization (spaCy)
2. POS tagging
3. Dependency parsing (extract verb-object pairs)
4. Named Entity Recognition
5. Deadline extraction (regex + date parsing)
6. Urgency keyword detection
7. Effort estimation (verb complexity)
8. Confidence scoring

---

## Frontend Documentation

### Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── BurnoutAlert.tsx      # Risk indicator
│   │   ├── GradientBackground.tsx
│   │   ├── Layout.tsx            # Main layout
│   │   ├── PrivateRoute.tsx      # Auth guard
│   │   ├── StatCard.tsx          # KPI cards
│   │   └── TaskCard.tsx          # Task display
│   ├── contexts/
│   │   └── AuthContext.tsx       # Auth state
│   ├── pages/
│   │   ├── AIAssistant.tsx       # Multi-agent chat
│   │   ├── Analytics.tsx         # Burnout analytics
│   │   ├── Dashboard.tsx         # Main overview
│   │   ├── Employees.tsx         # Employee management
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── TaskManagement.tsx    # Task CRUD
│   │   └── TeamView.tsx          # Manager dashboard
│   ├── services/
│   │   ├── analyticsService.ts
│   │   ├── multiAgentService.ts
│   │   └── taskService.ts
│   ├── types/
│   │   ├── Analytics.ts
│   │   ├── Employee.ts
│   │   └── Task.ts
│   ├── utils/
│   │   └── api.ts               # Axios config
│   ├── App.tsx
│   ├── index.tsx
│   └── theme.ts                 # MUI theme
├── package.json
└── .env.development
```

### Key Components

#### Layout Component
Main application layout with navigation drawer:
- Responsive design (mobile, tablet, desktop)
- Navigation menu
- User profile
- Logout functionality

#### TaskCard Component
Displays individual tasks with:
- Priority indicator (color-coded)
- Status badge
- Source badge (email, manual, etc.)
- Deadline countdown
- Quick actions

#### BurnoutAlert Component
Shows burnout risk with:
- Color-coded alerts (green/yellow/orange/red)
- Risk level display
- Recommendations
- Trend indicator

### Routing

```tsx
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  <Route element={<PrivateRoute />}>
    <Route path="/" element={<Dashboard />} />
    <Route path="/tasks" element={<TaskManagement />} />
    <Route path="/ai-assistant" element={<AIAssistant />} />
    <Route path="/analytics" element={<Analytics />} />
    <Route path="/team" element={<TeamView />} />
    <Route path="/employees" element={<Employees />} />
  </Route>
</Routes>
```

### State Management

Uses React Context API for:
- Authentication state
- User profile
- JWT token management

```tsx
const { user, token, login, logout } = useAuth();
```

### API Services

#### taskService.ts
```typescript
export const taskService = {
  getTasks: (params) => axios.get('/tasks', { params }),
  createTask: (data) => axios.post('/tasks', data),
  updateTask: (id, data) => axios.put(`/tasks/${id}`, data),
  deleteTask: (id) => axios.delete(`/tasks/${id}`),
  extractTasks: (text) => axios.post('/tasks/extract', { text }),
};
```

---

## Database Schema

### Core Models

#### Employee
```sql
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    productivity_periods JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_employees_email ON employees(email);
```

**Relationships**:
- Many-to-many with teams via employee_teams
- One-to-many with tasks (assigned_to)
- One-to-many with burnout_metrics
- One-to-many with achievements

#### Task
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    assigned_to UUID REFERENCES employees(id),
    created_by UUID REFERENCES employees(id),
    team_id UUID REFERENCES teams(id),
    urgency INTEGER CHECK (urgency BETWEEN 1 AND 5),
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    deadline TIMESTAMP,
    estimated_effort FLOAT,
    actual_effort FLOAT,
    status task_status NOT NULL,
    priority_score FLOAT,
    source task_source,
    dependencies JSON,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_team_id ON tasks(team_id);
```

**Enums**:
```sql
CREATE TYPE task_status AS ENUM (
    'pending', 'in_progress', 'completed', 'blocked', 'cancelled'
);

CREATE TYPE task_source AS ENUM (
    'email', 'meeting', 'manual', 'calendar', 'assigned'
);
```

#### Team
```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manager_id UUID REFERENCES employees(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### EmployeeTeam (Junction Table)
```sql
CREATE TABLE employee_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW(),
    is_primary BOOLEAN DEFAULT FALSE,
    UNIQUE(employee_id, team_id)
);

CREATE INDEX idx_employee_teams_employee_id ON employee_teams(employee_id);
CREATE INDEX idx_employee_teams_team_id ON employee_teams(team_id);
```

#### BurnoutMetric
```sql
CREATE TABLE burnout_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    date DATE NOT NULL,
    hours_worked FLOAT,
    cognitive_load FLOAT CHECK (cognitive_load BETWEEN 0 AND 1),
    breaks_taken INTEGER,
    social_interactions INTEGER,
    task_completion_rate FLOAT CHECK (task_completion_rate BETWEEN 0 AND 1),
    sentiment_score FLOAT CHECK (sentiment_score BETWEEN -1 AND 1),
    risk_score FLOAT CHECK (risk_score BETWEEN 0 AND 1),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_burnout_metrics_employee_id ON burnout_metrics(employee_id);
CREATE INDEX idx_burnout_metrics_date ON burnout_metrics(date);
```

#### Achievement
```sql
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    type achievement_type NOT NULL,
    description TEXT,
    impact_score FLOAT CHECK (impact_score BETWEEN 0 AND 1),
    recognized_by_manager BOOLEAN DEFAULT FALSE,
    recognition_note TEXT,
    related_task_id UUID REFERENCES tasks(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE achievement_type AS ENUM (
    'deliverable', 'innovation', 'client_feedback',
    'collaboration', 'learning'
);
```

---

## API Reference

### Authentication

#### POST /api/v1/auth/register
Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "role": "employee"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "employee"
}
```

#### POST /api/v1/auth/login
Authenticate and get JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Tasks

#### GET /api/v1/tasks
List tasks with filters.

**Query Parameters**:
- `assigned_to` (UUID): Filter by assignee
- `status` (string): pending, in_progress, completed, blocked, cancelled
- `team_id` (UUID): Filter by team
- `source` (string): email, meeting, manual, calendar, assigned
- `difficulty` (int): 1-5
- `min_urgency` (int): 1-5
- `max_urgency` (int): 1-5
- `skip` (int): Pagination offset
- `limit` (int): Results per page

**Response** (200):
```json
[
  {
    "id": "uuid",
    "title": "Implement authentication",
    "description": "...",
    "assigned_to": "uuid",
    "urgency": 5,
    "difficulty": 4,
    "deadline": "2025-12-01T10:00:00Z",
    "priority_score": 0.92,
    "status": "in_progress",
    "source": "manual"
  }
]
```

#### POST /api/v1/tasks
Create a new task.

**Request**:
```json
{
  "title": "Implement feature X",
  "description": "Detailed description",
  "assigned_to": "employee-uuid",
  "urgency": 4,
  "difficulty": 3,
  "deadline": "2025-12-01T10:00:00Z",
  "estimated_effort": 6,
  "team_id": "team-uuid"
}
```

**Response** (201):
```json
{
  "id": "new-task-uuid",
  "title": "Implement feature X",
  "priority_score": 0.78,
  ...
}
```

#### POST /api/v1/tasks/extract
Extract tasks from natural language text.

**Request**:
```json
{
  "text": "We need to finish the API documentation by Friday. Also, fix the authentication bug ASAP.",
  "context": "email",
  "employee_id": "uuid"
}
```

**Response** (200):
```json
{
  "tasks": [
    {
      "title": "Finish API documentation",
      "urgency": 3,
      "deadline": "2025-11-29",
      "estimated_effort": 4,
      "confidence": 0.85
    },
    {
      "title": "Fix authentication bug",
      "urgency": 5,
      "estimated_effort": 3,
      "confidence": 0.92
    }
  ]
}
```

### Analytics

#### GET /api/v1/analytics/burnout/{employee_id}
Get burnout risk analysis for an employee.

**Response** (200):
```json
{
  "employee_id": "uuid",
  "current_risk_score": 0.45,
  "risk_level": "medium",
  "factors": {
    "overwork": 0.5,
    "cognitive_overload": 0.6,
    "social_isolation": 0.3,
    "poor_completion": 0.2
  },
  "recommendations": [
    "Consider delegating some tasks",
    "Schedule regular breaks"
  ],
  "trend": "increasing"
}
```

#### GET /api/v1/analytics/team/{team_id}/equity
Get workload equity analysis for a team.

**Response** (200):
```json
{
  "team_id": "uuid",
  "equity_score": 0.85,
  "workload_distribution": [
    {
      "employee_id": "uuid1",
      "name": "Alice",
      "workload_score": 45.2,
      "task_count": 8
    },
    {
      "employee_id": "uuid2",
      "name": "Bob",
      "workload_score": 52.8,
      "task_count": 12
    }
  ],
  "recommendations": [
    "Consider reassigning tasks from Bob to Alice"
  ]
}
```

### Wellbeing

#### GET /api/v1/wellbeing/summary
Get complete wellbeing summary for current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "employee_id": "uuid",
  "metrics": {
    "workload_score": 12.5,
    "stress_level": 0.45,
    "cognitive_load": 0.62,
    "burnout_risk": 0.38
  },
  "task_summary": {
    "active_tasks": 8,
    "completed_this_week": 5
  },
  "overlap_analysis": {
    "overlap_count": 2,
    "conflicts": [
      {
        "task1": "Task A",
        "task2": "Task B",
        "hours_between": 6
      }
    ],
    "has_conflicts": true
  },
  "risk_level": "medium",
  "recommendations": [
    "High cognitive load. Try batching similar tasks.",
    "⚠️ 2 deadline conflicts detected."
  ]
}
```

### Multi-Agent System

#### POST /api/v1/agent/execute
Execute a request with intelligent agent routing.

**Request**:
```json
{
  "query": "What are my most urgent tasks?",
  "context": {
    "employee_id": "uuid"
  }
}
```

**Response** (200):
```json
{
  "agent_used": "priority_agent",
  "response": "Here are your top 3 urgent tasks:\n1. Fix authentication bug (urgency: 5)\n2. ...",
  "confidence": 0.92,
  "suggestions": ["Consider delegating task #3"]
}
```

#### GET /api/v1/agent/available
List all available agents.

**Response** (200):
```json
{
  "agents": [
    {
      "name": "priority_agent",
      "description": "Analyzes and suggests task priorities",
      "keywords": ["priority", "urgent", "important"]
    },
    {
      "name": "burnout_agent",
      "description": "Monitors employee wellbeing",
      "keywords": ["burnout", "stress", "wellbeing"]
    }
  ]
}
```

---

## Deployment

### Environment Variables

**Backend (.env)**:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/b2p_ai

# Security
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=production
DEBUG=false

# NLP
SPACY_MODEL=fr_core_news_lg

# Optional
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
```

**Frontend (.env.production)**:
```env
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
```

### Docker Deployment

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: b2p_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/b2p_ai
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Production Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=false
- [ ] Configure proper CORS origins
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure database backups
- [ ] Setup monitoring (Sentry, DataDog)
- [ ] Configure rate limiting
- [ ] Setup CDN for frontend assets
- [ ] Enable database connection pooling
- [ ] Configure log rotation
- [ ] Setup health check endpoints
- [ ] Enable Redis caching
- [ ] Configure email service (SendGrid, etc.)

---

## Development Guide

### Backend Development

**Running Tests**:
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

**Database Migrations**:
```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Adding a New API Endpoint**:

1. Create route in `app/api/v1/`:
```python
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router = APIRouter(prefix="/my-resource", tags=["my-resource"])

@router.get("/")
def list_resources(current_user: dict = Depends(get_current_user)):
    return {"resources": []}
```

2. Register in `app/main.py`:
```python
from app.api.v1 import my_resource

app.include_router(my_resource.router, prefix="/api/v1")
```

**Adding a New Service**:

1. Create service file in `app/services/`:
```python
class MyService:
    @staticmethod
    def do_something(data, db):
        # Business logic
        return result
```

2. Use in endpoint:
```python
from app.services.my_service import MyService

@router.post("/")
def create(data: Schema, db: Session = Depends(get_db)):
    result = MyService.do_something(data, db)
    return result
```

### Frontend Development

**Running Tests**:
```bash
cd frontend
npm test
npm test -- --coverage
```

**Adding a New Page**:

1. Create component in `src/pages/`:
```tsx
export default function MyPage() {
  return <div>My Page</div>;
}
```

2. Add route in `App.tsx`:
```tsx
<Route path="/my-page" element={<MyPage />} />
```

3. Add to navigation in `Layout.tsx`

**Creating a New API Service**:

```typescript
// src/services/myService.ts
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

export const myService = {
  getData: () => axios.get(`${API_URL}/my-resource`),
  createData: (data) => axios.post(`${API_URL}/my-resource`, data),
};
```

---

## Testing

### Backend Tests

**Unit Tests**:
```python
# tests/test_services.py
def test_priority_calculation():
    service = TaskPrioritizationService()
    score = service.calculate_priority(
        urgency=5,
        deadline=datetime.now() + timedelta(days=1),
        estimated_effort=4
    )
    assert 0 <= score <= 1
    assert score > 0.7  # High urgency + near deadline
```

**Integration Tests**:
```python
# tests/test_api.py
def test_create_task(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Test task", "urgency": 3},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert "priority_score" in response.json()
```

### Frontend Tests

**Component Tests**:
```tsx
// TaskCard.test.tsx
import { render, screen } from '@testing-library/react';
import TaskCard from './TaskCard';

test('renders task title', () => {
  const task = { title: 'Test Task', urgency: 3 };
  render(<TaskCard task={task} />);
  expect(screen.getByText('Test Task')).toBeInTheDocument();
});
```

---

## Security

### Authentication Flow

1. User submits credentials to `/auth/login`
2. Backend validates credentials
3. JWT token generated with user claims
4. Token returned to frontend
5. Frontend stores token (memory/localStorage)
6. All subsequent requests include: `Authorization: Bearer <token>`
7. Backend validates token on protected endpoints

### Security Best Practices

- **Password Hashing**: bcrypt with salt rounds
- **SQL Injection**: SQLAlchemy ORM prevents injection
- **XSS**: React auto-escapes content
- **CSRF**: Not applicable (token-based auth)
- **Rate Limiting**: Implement in production
- **Input Validation**: Pydantic schemas validate all inputs
- **HTTPS**: Required in production
- **CORS**: Configured allowed origins only

### Permission Levels

**Employee**:
- View own tasks, metrics, teams
- Create/update own tasks
- View team members

**Manager**:
- All employee permissions
- View team analytics
- Assign tasks to team members
- Access team wellbeing data

**Admin**:
- All manager permissions
- Manage all users
- Access all data
- System configuration

---

## Performance Optimization

### Database Optimization

**Indexing**:
- All foreign keys indexed
- Frequently queried columns indexed
- Composite indexes for common queries

**Query Optimization**:
```python
# Use eager loading to prevent N+1
employees = db.query(Employee).options(
    joinedload(Employee.teams),
    joinedload(Employee.tasks)
).all()

# Use pagination
tasks = db.query(Task).offset(skip).limit(limit).all()
```

**Connection Pooling**:
```python
# In config
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20
}
```

### Caching Strategy

**Redis Caching** (optional):
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_employee_metrics(employee_id: str):
    # Expensive calculation
    return metrics
```

**Frontend Caching**:
- React Query for API caching
- LocalStorage for user preferences
- Service Worker for offline support

### Frontend Performance

**Code Splitting**:
```tsx
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

**Memoization**:
```tsx
const MemoizedTaskCard = React.memo(TaskCard);
```

---

## Troubleshooting

### Common Issues

**Backend Won't Start**

Issue: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

Issue: `sqlalchemy.exc.OperationalError: could not connect`
```bash
# Solution: Check database is running
pg_isready
# Start PostgreSQL if needed
sudo systemctl start postgresql
```

**Frontend Won't Build**

Issue: `Module not found: Can't resolve '@mui/material'`
```bash
# Solution: Install dependencies
npm install
```

Issue: `CORS error when calling API`
```bash
# Solution: Add frontend URL to BACKEND_CORS_ORIGINS in .env
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**NLP Extraction Not Working**

Issue: `OSError: [E050] Can't find model 'fr_core_news_lg'`
```bash
# Solution: Download spaCy model
python -m spacy download fr_core_news_lg
```

### Logs

**Backend Logs**:
```bash
# Development
tail -f logs/app.log

# Production (Docker)
docker-compose logs -f backend
```

**Frontend Logs**:
- Browser console (F12)
- Network tab for API calls
- React DevTools for component inspection

---

## Contributing

### Code Style

**Backend**:
- Follow PEP 8
- Use type hints
- Document complex functions
- Keep functions < 50 lines

**Frontend**:
- Use TypeScript
- Follow Airbnb style guide
- Use functional components
- Props should have types

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

---

## License

MIT License - See LICENSE file for details

---

## Support

- **Issues**: GitHub Issues
- **Documentation**: This file
- **API Docs**: http://localhost:8000/docs

---

## Changelog

### Version 1.0.0 (2025-11-26)
- ✅ Complete multi-team support
- ✅ Wellbeing calculation system
- ✅ NLP task extraction (spaCy)
- ✅ Multi-agent orchestration
- ✅ Burnout detection
- ✅ Task prioritization
- ✅ Achievement tracking
- ✅ Email integration framework
- ✅ JWT authentication
- ✅ Responsive frontend

---

**Last Updated**: 2025-11-26
**Maintained by**: B2P.AI Development Team

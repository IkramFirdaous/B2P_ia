# B2P.AI - Bridge To Performance

<div align="center">

**AI-Powered Task Management & Burnout Prevention System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/react-18.2+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)](https://www.typescriptlang.org/)

</div>

---

## 🎯 Overview

B2P.AI is an intelligent workplace management system that combines AI-powered task prioritization with real-time burnout detection. It helps organizations optimize workload distribution, prevent employee burnout, and boost productivity through data-driven insights.

### Key Features

- 🤖 **AI Task Prioritization**: Automatic task scoring based on urgency, deadlines, effort, and employee productivity patterns
- 🧠 **NLP Task Extraction**: Extract tasks from emails and meeting notes using Natural Language Processing
- 📊 **Burnout Detection**: Real-time monitoring of employee wellbeing indicators with predictive analytics
- ⚖️ **Workload Balancing**: Equitable task distribution across teams with automated recommendations
- 🏆 **Achievement Tracking**: Automatic recognition of employee accomplishments
- 📈 **Advanced Analytics**: Comprehensive dashboards for managers and individuals

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL (Database)
- Redis (Cache & Task Queue)
- SQLAlchemy (ORM)
- spaCy & Transformers (NLP/ML)
- Celery (Background Tasks)

**Frontend:**
- React 18 + TypeScript
- Material-UI
- Redux Toolkit (State Management)
- Recharts (Visualizations)
- Axios (API Client)

**DevOps:**
- Docker & Docker Compose
- CI/CD Ready

---

## 📁 Project Structure

```
b2p-ai/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API Endpoints
│   │   ├── models/         # Database Models
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # Business Logic
│   │   ├── ml/             # ML Models
│   │   └── core/           # Configuration
│   ├── tests/              # Test Suite
│   └── requirements.txt
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable Components
│   │   ├── pages/         # Page Components
│   │   ├── services/      # API Services
│   │   ├── types/         # TypeScript Types
│   │   └── store/         # Redux Store
│   └── package.json
│
├── ml_models/             # Pre-trained ML Models
├── docs/                  # Documentation
├── docker-compose.yml     # Container Orchestration
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/b2p-ai.git
cd b2p-ai

# Start all services
docker-compose up -d

# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

#### Option 2: Manual Setup

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download fr_core_news_lg

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm start
```

---

## 🔧 Configuration

### Backend Configuration (`.env`)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/b2p_ai

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Environment
ENVIRONMENT=development
```

### Frontend Configuration (`.env`)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/employee/{id}/prioritized` - Get prioritized tasks
- `POST /api/v1/tasks/extract` - Extract tasks from text (NLP)

#### Analytics
- `GET /api/v1/analytics/burnout/{employee_id}` - Get burnout risk
- `GET /api/v1/analytics/team/{team_id}/equity` - Team workload equity
- `POST /api/v1/analytics/track-activity` - Track daily activity

#### Employees
- `POST /api/v1/employees` - Create employee
- `GET /api/v1/employees/{id}/stats` - Get employee statistics

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

---

## 🤖 AI Features

### 1. Task Prioritization Algorithm

```
Priority Score = 0.3×Urgency + 0.25×(1/Deadline) + 0.2×Effort
                + 0.15×Productivity + 0.1×Dependencies
```

### 2. Burnout Risk Calculation

```
Risk = 0.3×Hours + 0.25×CognitiveLoad + 0.2×Isolation
      + 0.1×TaskCompletion + 0.15×Sentiment
```

### 3. Workload Equity

```
Global Score = 0.6 × Cumulative_Load + 0.4 × Critical_Score
```

---

## 🗺️ Roadmap

### Phase 1: MVP Core ✅
- [x] Database models and schemas
- [x] Core services (prioritization, burnout, balancing)
- [x] API endpoints
- [x] Basic frontend structure

### Phase 2: AI Features 🚧
- [ ] NLP task extraction (spaCy integration)
- [ ] Sentiment analysis
- [ ] ML burnout prediction model
- [ ] Skill gap analysis

### Phase 3: Advanced Features 🔜
- [ ] Real-time notifications
- [ ] Calendar integration
- [ ] Email integration
- [ ] Mobile app
- [ ] Advanced visualizations

### Phase 4: Production 🔜
- [ ] Complete test coverage
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Deployment automation

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Material-UI for the beautiful React components
- spaCy for NLP capabilities
- The open-source community

---

<div align="center">

**Made with ❤️ for better workplace wellbeing**

</div>
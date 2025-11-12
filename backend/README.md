# B2P.AI Backend

Backend API for Bridge To Performance - AI-powered task management and burnout prevention system.

## Features

- **Intelligent Task Prioritization**: Automatic task scoring based on urgency, deadlines, effort, and productivity patterns
- **Burnout Detection**: Real-time monitoring of employee wellbeing indicators
- **NLP Task Extraction**: Automatic task extraction from emails and meeting notes
- **Workload Balancing**: Equitable distribution of tasks across teams
- **Skills Management**: Gap analysis and training recommendations

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML/AI**: spaCy, Transformers, scikit-learn
- **Task Queue**: Celery

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Download spaCy language model:
```bash
python -m spacy download fr_core_news_lg
```

5. Initialize database:
```bash
alembic upgrade head
```

### Running

Development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
pytest tests/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── ml/           # ML models
│   ├── core/         # Core configuration
│   └── utils/        # Utilities
├── tests/            # Test suite
└── requirements.txt
```

## License

MIT

# Database Setup Guide

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# 1. Start PostgreSQL only
docker-compose up -d postgres

# 2. Wait 10 seconds for database to be ready, then run migrations
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 3. Verify database is set up
alembic current
```

### Option 2: Manual PostgreSQL Installation

If you have PostgreSQL installed locally:

1. **Create database and user:**
```sql
CREATE USER b2p_user WITH PASSWORD 'b2p_password';
CREATE DATABASE b2p_ai OWNER b2p_user;
GRANT ALL PRIVILEGES ON DATABASE b2p_ai TO b2p_user;
```

2. **Ensure your `.env` matches:**
```env
DATABASE_URL=postgresql://b2p_user:b2p_password@localhost:5432/b2p_ai
```

3. **Run migrations:**
```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Troubleshooting

### "Connection refused" or "Port 5432 already in use"
```bash
# Check if PostgreSQL is running
docker ps

# Check what's using port 5432
netstat -ano | findstr :5432

# If another PostgreSQL is running, stop it or change the port in docker-compose.yml
```

### "Password authentication failed"
- Ensure `.env` DATABASE_URL matches docker-compose.yml credentials
- Current credentials:
  - User: `b2p_user`
  - Password: `b2p_password`
  - Database: `b2p_ai`

### Check Migration Status
```bash
cd backend
alembic current  # Show current migration
alembic history  # Show all migrations
```

### Reset Database (⚠️ Destroys all data)
```bash
# Stop and remove containers
docker-compose down -v

# Start fresh
docker-compose up -d postgres

# Recreate migrations
cd backend
alembic upgrade head
```

## What Gets Created

The migration will create these tables:

1. **employees** - User accounts and employee data
2. **teams** - Team/department information
3. **employee_teams** - Many-to-many relationship (employees ↔ teams)
4. **tasks** - Task management
5. **burnout_metrics** - Daily wellbeing tracking
6. **achievements** - Employee accomplishments
7. **skills** - Master skill list
8. **employee_skills** - Employee skill proficiency

## Next Steps

After successful migration:

1. **Start backend server:**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Access API docs:**
- http://localhost:8000/docs

3. **Create first user:**
```bash
POST http://localhost:8000/api/v1/auth/register
{
  "email": "admin@example.com",
  "password": "securepassword",
  "name": "Admin User",
  "role": "admin"
}
```

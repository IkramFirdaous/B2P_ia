# 🚀 Quick Start Guide - B2P.AI

Get your B2P.AI application running in minutes!

## Prerequisites

- Node.js 18+ installed
- Python 3.11+ installed
- PostgreSQL 14+ running (or use Docker)

## Option 1: Frontend Only (Quick Demo)

Want to see the beautiful UI immediately? Just run the frontend with mock data:

```bash
cd frontend
npm install
npm start
```

Visit http://localhost:3000 and explore the interface! 🎨

The frontend works with mock data, so you can see all features without the backend.

## Option 2: Full Stack with Docker

Run everything at once:

```bash
docker-compose up -d
```

Then visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Option 3: Manual Setup (Development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env

# Start server
uvicorn app.main:app --reload
```

Backend will be at http://localhost:8000

### Frontend Setup (separate terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be at http://localhost:3000

## 🎯 What You Can Do

### Dashboard
- View your tasks prioritized by AI
- Monitor your burnout risk score
- Track recent achievements
- See quick statistics

### Tasks Page
- Create and manage tasks
- Filter by status (pending, in progress, completed)
- Search tasks
- View AI-calculated priority scores

### Team View (Manager)
- See team workload distribution
- Monitor team members' burnout risk
- Identify overloaded team members
- Trigger workload rebalancing

### Analytics
- View burnout risk trends
- Analyze productivity patterns
- See task distribution charts
- Track contributing risk factors

## 🎨 Design Features

- Modern gradient colors (purple theme)
- Smooth animations and transitions
- Fully responsive (mobile, tablet, desktop)
- Beautiful charts with Recharts
- Intuitive navigation
- Card-based layout

## 🔥 Hot Tips

1. The UI is fully functional with mock data - no backend needed to explore!
2. All pages are responsive - try resizing your browser
3. Hover over cards and buttons to see nice animations
4. The navigation sidebar adapts to mobile with a hamburger menu

## Need Help?

Check the main README.md for detailed documentation and API endpoints.

---

**Enjoy exploring B2P.AI!** 🎉

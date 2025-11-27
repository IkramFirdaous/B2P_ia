"""FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered task management and burnout prevention system",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    init_db()

    # Start email worker if configured
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        from app.workers.email_worker import start_email_worker
        try:
            start_email_worker(check_interval_minutes=5)
            print("Email worker started successfully")
        except Exception as e:
            print(f"Failed to start email worker: {e}")

    print("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Application shutting down...")

    # Stop email worker
    from app.workers.email_worker import stop_email_worker
    try:
        stop_email_worker()
        print("Email worker stopped")
    except:
        pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Import and include API routers
from app.api.v1 import tasks, employees, analytics, agent, email, teams, auth, wellbeing

# Authentication router (no auth required for these endpoints)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["authentication"])

# Other routers
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["tasks"])
app.include_router(employees.router, prefix=settings.API_V1_PREFIX, tags=["employees"])
app.include_router(teams.router, prefix=settings.API_V1_PREFIX, tags=["teams"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["analytics"])
app.include_router(wellbeing.router, prefix=settings.API_V1_PREFIX, tags=["wellbeing"])
app.include_router(agent.router, prefix=settings.API_V1_PREFIX, tags=["multi-agent"])
app.include_router(email.router, prefix=settings.API_V1_PREFIX, tags=["email-integration"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

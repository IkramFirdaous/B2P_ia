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

    # Initialize database (optional - will work without DB for API testing)
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("⚠️  Backend will run without database (limited functionality)")
        print("⚠️  To enable database: Set DATABASE_URL in .env or use SQLite")

    print("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Application shutting down...")


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
from app.api.v1 import tasks, employees, analytics, agent, email_extraction

app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["tasks"])
app.include_router(employees.router, prefix=settings.API_V1_PREFIX, tags=["employees"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["analytics"])
app.include_router(agent.router, prefix=settings.API_V1_PREFIX, tags=["multi-agent"])
app.include_router(email_extraction.router, prefix=settings.API_V1_PREFIX, tags=["email-extraction"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.weather import router as weather_router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Weather AI Agent API",
        "docs": "/docs",
        "version": settings.VERSION
    }
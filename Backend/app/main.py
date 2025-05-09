from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.weather import router as weather_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(weather_router, prefix="/api/weather", tags=["Weather"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Weather AI Agent API",
        "docs": "/docs",
        "version": settings.VERSION
    }
    
# Local development (only runs when executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=int(settings.API_PORT), reload=settings.DEBUG)
    
# uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload    
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings, STATIC_DIR
from app.database import init_db, log_event
from app.character.assets_manager import initialize_character_assets
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_content import router as content_router
from app.api.routes_workflow import router as workflow_router
from app.api.routes_youtube import router as youtube_router
from app.api.routes_settings import router as settings_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mysteryverse.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MYSTERYVERSE AI Autonomous Media Suite...")
    init_db()
    try:
        initialize_character_assets()
        logger.info("Character assets initialized successfully.")
    except Exception as e:
        logger.warning("Could not initialize character sprites on startup: %s", e)

    log_event("INFO", "System", "MYSTERYVERSE AI Backend Server Initialized")
    logger.info("Autonomous Workflow Scheduler ready in on-demand mode.")
    
    yield
    # Shutdown
    logger.info("Shutting down MYSTERYVERSE AI...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for media streaming (videos, audio, thumbnails, character sprites)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount API Routers
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(content_router, prefix=settings.API_PREFIX)
app.include_router(workflow_router, prefix=settings.API_PREFIX)
app.include_router(youtube_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }

"""
Aura-26 Stadium Pulse Main Application Entrypoint.

WHY: Centralized FastAPI app initialization with CORS middleware and static asset mounting
ensures a single, lightweight binary entrypoint (< 1MB total codebase) capable of serving
both high-throughput async REST endpoints and an accessible, responsive operations dashboard.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.api.endpoints import router as api_router

# Load settings at startup
settings = get_settings()

# Initialize high-performance FastAPI application
app = FastAPI(
    title="Aura-26 Stadium Pulse API",
    description="Context-Aware GenAI Crowd Flow & Operations Assistant for FIFA World Cup 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# WHY: Configure CORS to allow cross-origin requests from concourse displays and command center tablets.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to stadium intranet domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API endpoints
app.include_router(api_router)

# Resolve absolute path to static directory for reliable mounting across environments
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Mount static directory for CSS, JS, and image assets (if needed)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", summary="Serve Operations Dashboard UI", response_class=FileResponse)
async def serve_dashboard():
    """
    Root route serving the vanilla HTML5/CSS/JS Operations Dashboard.
    WHY: Serving vanilla web assets directly from FastAPI eliminates Node/Vite build steps,
    guarantees zero node_modules bloat, and keeps total repository footprint well under 10MB.
    """
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"error": "Dashboard index.html not found in static directory."}
    return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    # WHY: Direct module invocation allows simple local testing via 'python3 -m app.main'
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=(settings.app_env == "development"),
        log_level=settings.log_level.lower()
    )

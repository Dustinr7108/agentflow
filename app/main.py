"""AgentFlow - AI Agent Orchestration Platform.

The platform where non-technical users design AI agent workflows
visually, like Zapier but for AI agents.
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.db import init_db
from app.seed import seed_builtin_agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    seed_builtin_agents()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Visual AI Agent Orchestration Platform - Design, run, and automate AI workflows",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://awesomeai.life",
        "https://www.awesomeai.life",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
from app.routers.auth_router import router as auth_router
from app.routers.workflow_router import router as workflow_router
from app.routers.agent_router import router as agent_router
from app.routers.template_router import router as template_router
from app.routers.billing_router import router as billing_router

app.include_router(auth_router)
app.include_router(workflow_router)
app.include_router(agent_router)
app.include_router(template_router)
app.include_router(billing_router)


@app.get("/health")
def health():
    return {"status": "healthy"}


# Serve frontend static files in production
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    # Catch-all: serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # Don't intercept API routes or docs
        if full_path.startswith(("auth/", "workflows/", "agents/", "templates/", "billing/", "docs", "openapi", "health")):
            return None
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }

"""AgentFlow - AI Agent Orchestration Platform.

The platform where non-technical users design AI agent workflows
visually, like Zapier but for AI agents.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
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


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

# AgentFlow - AI Agent Orchestration Platform

Visual platform for designing, running, and automating AI agent workflows.
Like Zapier meets AI agents - drag, drop, connect, run.

## Features

- **Visual Workflow Designer** - Drag-and-drop React Flow canvas
- **6 Agent Types** - LLM, Web Search, Code Execution, API Call, Data Transform, Conditional
- **Pre-built Templates** - Lead research, content pipeline, competitor analysis, smart alerts
- **Conditional Branching** - If/else logic for intelligent routing
- **Usage Tracking** - Token counts, costs, run history per workflow
- **Stripe Billing** - Free/Starter/Pro/Enterprise tiers with usage limits
- **JWT Auth** - Secure user accounts with bcrypt passwords
- **Multi-Provider AI** - OpenAI, Anthropic, or local Ollama

## Quick Start

### 1. Clone and configure
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker
```bash
docker-compose up --build
```

### 3. Access
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

### Without Docker
```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Architecture

```
Backend (FastAPI)          Frontend (React + React Flow)
+------------------+      +----------------------+
| Auth (JWT)       |      | Login / Register     |
| Workflow CRUD    |<---->| Dashboard            |
| Workflow Engine  |      | Visual Editor        |
| Agent Registry   |      | Template Gallery     |
| Billing (Stripe) |      | Run Results Panel    |
+------------------+      +----------------------+
        |
  +-----+------+
  |  PostgreSQL |
  |    Redis    |
  +------------+
```

## Agent Types

| Type | Description |
|------|-------------|
| `llm` | Language model for text tasks (OpenAI/Anthropic/Ollama) |
| `web_search` | DuckDuckGo web search |
| `code_exec` | Sandboxed Python execution |
| `api_call` | HTTP requests to any REST API |
| `data_transform` | Filter, map, merge, reshape data |
| `conditional` | If/else branching logic |

## Pricing

| Plan | Price | Runs/Month |
|------|-------|------------|
| Free | $0 | 10 |
| Starter | $29/mo | 100 |
| Pro | $99/mo | 1,000 |
| Enterprise | $299/mo | 10,000 |

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Celery
- **Frontend**: React 18, TypeScript, React Flow, Tailwind CSS, Zustand
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **AI**: OpenAI, Anthropic, Ollama
- **Payments**: Stripe
- **Deploy**: Docker Compose, Railway, Vercel

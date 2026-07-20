# CLAUDE.md — StockWise AI Stock Investment Learning Platform

## Project Overview

StockWise is a multi-agent AI platform for learning stock investment. Three specialized agents (Financial Report, News Analysis, Market Data) analyze stocks through the Claude API and explain everything in beginner-friendly language.

## Architecture

```
Frontend (Next.js 15) → API Proxy → Backend (FastAPI) → Claude API + yfinance
```

- **Frontend**: `apps/frontend/` — Next.js 15 App Router, TypeScript, Tailwind CSS
- **Backend**: `apps/backend/` — Python 3.12, FastAPI, Anthropic SDK
- **Monorepo**: Turborepo + pnpm workspaces

## Running Locally

### Backend
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp ../../.env.example ../../.env  # Then edit .env with ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd apps/frontend
pnpm install
pnpm dev  # Starts on localhost:3000
```

### Docker
```bash
docker compose up
```

## Key Files

### Backend
- `app/main.py` — FastAPI app factory with CORS, lifespan, health check
- `app/config.py` — pydantic-settings (env vars)
- `app/agents/base.py` — BaseAgent with Claude API tool-use loop
- `app/agents/orchestrator.py` — MultiAgentOrchestrator (routes queries, coordinates agents)
- `app/agents/prompts.py` — System prompts for all 3 agents + orchestrator
- `app/agents/tool_schemas.py` — JSON Schema tool definitions
- `app/tools/` — Tool implementations (what agents can actually do)
- `app/services/` — Data fetching (yfinance, EDGAR, news, technical analysis)
- `app/schemas/` — Pydantic request/response models

### Frontend
- `src/app/layout.tsx` — Root layout
- `src/app/page.tsx` — Landing page with hero search
- `src/app/(dashboard)/layout.tsx` — Dashboard sidebar + nav
- `src/app/(dashboard)/page.tsx` — Dashboard home (market overview)
- `src/app/(dashboard)/stock/[symbol]/page.tsx` — Stock analysis with 4 tabs
- `src/app/(dashboard)/chat/page.tsx` — Chat with SSE streaming
- `src/app/(dashboard)/learn/page.tsx` — Educational glossary

## Agent System

### Three Specialized Agents
1. **Financial Report Agent** — SEC filings, balance sheets, key ratios, plain-English explanations
2. **News Analysis Agent** — Fetches news, sentiment analysis, reasoning chains
3. **Market Data Agent** — Technical indicators, trends, buy/sell/hold recommendations

### Orchestration Modes
- **SINGLE**: Query classified and routed to one agent
- **SEQUENTIAL**: News → Financial → Market (each receives prior context)
- **PARALLEL**: All three run independently, then synthesized

### Agentic Loop
```
User query → Claude message with tools → Tool calls → Execute tools in parallel → Send results → Repeat → Final response
```

## Data Sources
- `yfinance` — Primary (free, no key): prices, history, financials, news
- `edgartools` — SEC EDGAR: official filings, XBRL-parsed financials
- Alpha Vantage — Optional: enhanced news sentiment (requires API key)

## Environment Variables
- `ANTHROPIC_API_KEY` — **Required** — Claude API key
- `ANTHROPIC_MODEL` — Default: `claude-sonnet-4-6`
- `ALPHA_VANTAGE_API_KEY` — Optional — Enhanced news data
- `DATABASE_URL` — Default: SQLite (`sqlite+aiosqlite:///./stockwise.db`)

## Design Decisions
- **No LangChain** — Manual agentic loop with Anthropic SDK is simpler
- **SQLite for MVP** — Zero setup; migrate to PostgreSQL for production
- **yfinance primary** — Free, no API key, sufficient for learning
- **No auth** — Session-based; learning tool, not portfolio tracker
- **SSE streaming** — Chat responses stream agent-by-agent

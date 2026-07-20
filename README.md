# StockWise — AI Stock Investment Learning Platform

An AI-powered platform for learning stock investment and financial management. Built with a multi-agent architecture powered by Claude, StockWise helps beginners understand company financials, market news, and technical analysis through clear, educational explanations.

## Features

- **Multi-Agent Analysis**: Three specialized AI agents analyze stocks from different angles:
  - 📊 **Financial Report Agent** — Analyzes SEC filings, balance sheets, income statements, key ratios
  - 📰 **News Analysis Agent** — Fetches financial news, performs sentiment analysis, predicts market impact
  - 📈 **Market Data Agent** — Technical indicators, price trends, buy/sell/hold recommendations
- **Interactive Chat**: Ask investment questions and get multi-agent responses with streaming
- **Stock Charts**: Professional candlestick charts with technical indicators
- **Watchlist**: Track stocks you're interested in
- **Educational**: Every term defined in plain English — built for beginners

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, Anthropic SDK |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Data | yfinance, SEC EDGAR (edgartools) |
| Charts | TradingView Lightweight Charts, Recharts |
| AI | Claude (via Anthropic API) |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### 🚀 One-Click Launch

**Windows:** Double-click `start.bat`  
**Mac / Linux:** Run `./start.sh`  
**Any OS:** Run `pnpm dev` at the project root

The launcher will:
1. Check prerequisites (Python, Node.js)
2. Create `.env` from template if needed (prompts for your API key)
3. Set up Python virtual environment + install deps
4. Install frontend dependencies
5. Start backend (port 8000) + frontend (port 3000)
6. Open http://localhost:3000 in your browser

**First time only:** Edit `.env` and set `ANTHROPIC_API_KEY=sk-ant-...` before launching.

### Manual Setup

```bash
cd stockwise

# 1. Set your API key
cp .env.example .env
# → Edit .env, paste your ANTHROPIC_API_KEY

# 2. Backend
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd apps/frontend
npm install -g pnpm  # if you don't have pnpm
pnpm install
pnpm dev
```

### Docker

```bash
docker compose up
```

## Project Structure

```
stockwise/
├── apps/
│   ├── backend/          # FastAPI application
│   └── frontend/         # Next.js application
├── docker/               # Docker configs
└── packages/             # Shared packages
```

## License

MIT

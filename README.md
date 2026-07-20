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
- pnpm
- An Anthropic API key

### Setup

```bash
# Clone and enter the project
cd stockwise

# Copy environment file and add your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY

# Backend
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (in a new terminal)
cd apps/frontend
pnpm install
pnpm dev
```

Open http://localhost:3000 to use StockWise.

### Docker (alternative)

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

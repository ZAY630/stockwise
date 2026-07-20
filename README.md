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

## How to Run

### Step 1: Prerequisites

Make sure you have these installed:

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.12+ | `python --version` |
| Node.js | 20+ | `node --version` |

You also need an [Anthropic API key](https://console.anthropic.com) for Claude.

### Step 2: Set your API key

```bash
# Copy the example env file
cp .env.example .env
```

Then open `.env` in any text editor and replace the placeholder:

```env
ANTHROPIC_API_KEY=sk-ant-your-real-key-here   # ← paste your key
```

That's the only key you need. Leave `ALPHA_VANTAGE_API_KEY` blank — it's optional.

### Step 3: Launch

Pick one:

| Method | Command | Best for |
|--------|---------|----------|
| **Windows** | Double-click `start.bat` | One-click, no terminal needed |
| **Mac / Linux** | `./start.sh` | Single terminal window, Ctrl+C to stop |
| **Any OS** | `pnpm dev` | If you already have pnpm installed |
| **Docker** | `docker compose up` | If you prefer containers |

On first run, the launcher automatically:
- Creates a Python virtual environment (`.venv/`)
- Installs all Python dependencies
- Installs all frontend dependencies (`node_modules/`)
- Starts the backend on **http://localhost:8000**
- Starts the frontend on **http://localhost:3000**
- Opens the app in your browser

On subsequent runs it starts instantly — no setup repeated.

### Step 4: Use the app

Open **http://localhost:3000** and you'll see:

| Page | What you can do |
|------|----------------|
| **Dashboard** (`/dashboard`) | View popular stocks with live prices |
| **Stock Detail** (`/dashboard/stock/AAPL`) | Full AI analysis with 4 tabs (Full / Market / Financial / News) |
| **Chat** (`/dashboard/chat`) | Ask questions, get streaming multi-agent responses |
| **Learn** (`/dashboard/learn`) | Glossary of 15+ financial terms with plain-English definitions |
| **Watchlist** (`/dashboard/watchlist`) | Track stocks you're interested in |

### Manual start (if you prefer separate terminals)

```bash
# Terminal 1 — Backend
cd apps/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd apps/frontend
npm install -g pnpm              # skip if you have pnpm
pnpm install
pnpm dev
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

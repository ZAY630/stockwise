#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  StockWise - AI Stock Investment Platform${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || {
    echo -e "${RED}[ERROR] Python 3.12+ is required. Install from https://python.org${NC}"
    exit 1
}
PYTHON=$(command -v python3 || command -v python)

command -v node >/dev/null 2>&1 || {
    echo -e "${RED}[ERROR] Node.js 20+ is required. Install from https://nodejs.org${NC}"
    exit 1
}

# Find pnpm or install it
if ! command -v pnpm >/dev/null 2>&1; then
    echo -e "${YELLOW}[*] Installing pnpm...${NC}"
    npm install -g pnpm
fi

# Check .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARNING] .env not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}[ACTION] Edit .env and add your ANTHROPIC_API_KEY, then re-run this script.${NC}"
    exit 1
fi

if grep -q "ANTHROPIC_API_KEY=your-api-key-here" .env 2>/dev/null; then
    echo -e "${RED}[ERROR] ANTHROPIC_API_KEY is not set in .env!${NC}"
    echo -e "${RED}[ACTION] Edit .env and replace 'your-api-key-here' with your real API key.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Prerequisites checked${NC}"

# Setup backend
echo ""
echo -e "${BLUE}--- Setting up Backend ---${NC}"
cd apps/backend

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[*] Creating Python virtual environment...${NC}"
    $PYTHON -m venv .venv
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
fi

echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
pip install -q -e ".[dev]"
echo -e "${GREEN}[✓] Backend dependencies ready${NC}"

# Setup frontend
echo ""
echo -e "${BLUE}--- Setting up Frontend ---${NC}"
cd ../../apps/frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[*] Installing frontend dependencies...${NC}"
    pnpm install
    echo -e "${GREEN}[✓] Frontend dependencies installed${NC}"
fi

cd ../..

# Launch
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting StockWise...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  Backend  → ${GREEN}http://localhost:8000${NC}"
echo -e "  Frontend → ${GREEN}http://localhost:3000${NC}"
echo -e "  API Docs → ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Press ${RED}Ctrl+C${NC} to stop all servers."
echo -e "${BLUE}========================================${NC}"
echo ""

# Trap to kill both processes on Ctrl+C
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down StockWise...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}StockWise stopped.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
cd apps/backend
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../..

# Brief pause
sleep 2

# Start frontend
cd apps/frontend
pnpm dev &
FRONTEND_PID=$!
cd ../..

# Open browser (platform-specific)
sleep 3
case "$(uname -s)" in
    Darwin)    open http://localhost:3000 ;;
    Linux)     xdg-open http://localhost:3000 2>/dev/null || echo -e "${YELLOW}Open http://localhost:3000 in your browser${NC}" ;;
    MINGW*|MSYS*|CYGWIN*)  start http://localhost:3000 2>/dev/null || echo -e "${YELLOW}Open http://localhost:3000 in your browser${NC}" ;;
esac

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID

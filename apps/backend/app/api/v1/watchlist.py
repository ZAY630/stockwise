"""Watchlist CRUD endpoints (placeholder — full impl in Phase 3)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_watchlists():
    """List all watchlists."""
    return {"watchlists": [], "message": "Watchlist feature coming in Phase 3"}


@router.post("")
async def create_watchlist():
    """Create a new watchlist."""
    return {"message": "Watchlist feature coming in Phase 3"}


@router.post("/items")
async def add_stock_to_watchlist():
    """Add a stock to a watchlist."""
    return {"message": "Watchlist feature coming in Phase 3"}

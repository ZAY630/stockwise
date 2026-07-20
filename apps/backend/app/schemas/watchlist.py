"""Watchlist-related Pydantic schemas (full implementation in Phase 3)."""

from datetime import datetime

from pydantic import BaseModel


class WatchlistItemCreate(BaseModel):
    """Request to add a stock to a watchlist."""

    symbol: str
    watchlist_id: str | None = None
    notes: str = ""


class WatchlistItemResponse(BaseModel):
    """A watchlist item."""

    id: str
    symbol: str
    added_at: datetime
    notes: str


class WatchlistCreate(BaseModel):
    """Request to create a new watchlist."""

    name: str


class WatchlistResponse(BaseModel):
    """A watchlist with its items."""

    id: str
    name: str
    created_at: datetime
    items: list[WatchlistItemResponse] = []

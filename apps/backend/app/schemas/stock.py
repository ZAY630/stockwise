"""Stock-related Pydantic schemas."""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single search result for stock lookup."""

    symbol: str
    name: str
    exchange: str = ""
    type: str = ""


class StockInfoResponse(BaseModel):
    """Comprehensive stock information."""

    symbol: str
    name: str
    sector: str = ""
    industry: str = ""
    market_cap: float | None = None
    description: str = ""
    website: str = ""


class PriceResponse(BaseModel):
    """Current stock price and daily statistics."""

    symbol: str
    price: float
    change: float
    change_percent: float
    previous_close: float
    open: float
    day_high: float
    day_low: float
    volume: int
    fifty_two_week_high: float
    fifty_two_week_low: float


class OHLCVPoint(BaseModel):
    """A single OHLCV data point for charts."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoryResponse(BaseModel):
    """Historical price data response."""

    symbol: str
    period: str
    interval: str
    data: list[OHLCVPoint]

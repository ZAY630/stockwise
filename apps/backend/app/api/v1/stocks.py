"""Stock data endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.stock import PriceResponse, SearchResult, StockInfoResponse
from app.services.yfinance_service import YFinanceService

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
async def search_stocks(q: str = Query(..., min_length=1, description="Search query")):
    """Search for stocks by name or ticker symbol."""
    try:
        results = await YFinanceService.search_ticker(q)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=StockInfoResponse)
async def get_stock_info(symbol: str):
    """Get comprehensive information about a stock."""
    try:
        info = await YFinanceService.get_stock_info(symbol.upper())
        return StockInfoResponse(
            symbol=symbol.upper(),
            name=info.get("longName", ""),
            sector=info.get("sector", ""),
            industry=info.get("industry", ""),
            market_cap=info.get("marketCap"),
            description=info.get("longBusinessSummary", ""),
            website=info.get("website", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch data for {symbol}: {str(e)}")


@router.get("/{symbol}/price", response_model=PriceResponse)
async def get_stock_price(symbol: str):
    """Get current price and daily change for a stock."""
    try:
        fi = await YFinanceService.get_fast_info(symbol.upper())
        return PriceResponse(
            symbol=symbol.upper(),
            price=fi.get("lastPrice", 0) or fi.get("regularMarketPreviousClose", 0),
            change=(fi.get("lastPrice", 0) or 0) - (fi.get("regularMarketPreviousClose", 0) or 0),
            change_percent=(
                (((fi.get("lastPrice", 0) or 0) - (fi.get("regularMarketPreviousClose", 0) or 0))
                 / (fi.get("regularMarketPreviousClose", 1) or 1)) * 100
            ),
            previous_close=fi.get("regularMarketPreviousClose", 0),
            open=fi.get("open", 0),
            day_high=fi.get("dayHigh", 0),
            day_low=fi.get("dayLow", 0),
            volume=fi.get("lastVolume", 0),
            fifty_two_week_high=fi.get("yearHigh", 0),
            fifty_two_week_low=fi.get("yearLow", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}: {str(e)}")


@router.get("/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1y", description="Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)"),
    interval: str = Query("1d", description="Data interval (1d, 1wk, 1mo)"),
):
    """Get historical OHLCV data for charting."""
    try:
        data = await YFinanceService.get_historical_data(
            symbol.upper(), period=period, interval=interval
        )
        return {"symbol": symbol.upper(), "period": period, "interval": interval, "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not fetch history for {symbol}: {str(e)}")

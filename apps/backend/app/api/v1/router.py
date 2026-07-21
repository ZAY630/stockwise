"""API v1 router — aggregates all sub-routers."""

from fastapi import APIRouter, Query

from app.api.v1 import analysis, chat, stocks, watchlist
from app.market_config import MARKETS, DEFAULT_MARKET, get_market

api_v1_router = APIRouter()

api_v1_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_v1_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_v1_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])


@api_v1_router.get("/market")
async def get_market_info(market: str = Query(DEFAULT_MARKET, description="Market code: us or cn")):
    """Get market configuration — popular tickers, currency, language."""
    cfg = get_market(market)
    return {
        "code": cfg.code,
        "name_en": cfg.name_en,
        "name_native": cfg.name_native,
        "currency": cfg.currency,
        "currency_symbol": cfg.currency_symbol,
        "locale": cfg.locale,
        "popular_tickers": [
            {"symbol": s, "name": cfg.ticker_names.get(s, "")}
            for s in cfg.popular_tickers
        ],
        "indices": [
            {"symbol": i, "name": cfg.index_names.get(i, "")}
            for i in cfg.indices
        ],
    }

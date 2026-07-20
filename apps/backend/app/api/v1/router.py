"""API v1 router — aggregates all sub-routers."""

from fastapi import APIRouter

from app.api.v1 import analysis, chat, stocks, watchlist

api_v1_router = APIRouter()

api_v1_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_v1_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_v1_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

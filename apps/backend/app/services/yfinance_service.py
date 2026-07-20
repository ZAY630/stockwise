"""Yahoo Finance data service using yfinance library.

This is the primary data source for StockWise. It requires no API key
and provides price data, fundamentals, news, and more.
"""

import asyncio
from datetime import datetime
from typing import Any

import yfinance as yf

from app.config import settings
from app.middleware.error_handler import DataUnavailableError, InvalidSymbolError
from app.services.cache_service import cache


class YFinanceService:
    """Wrapper around yfinance for async, cached access to Yahoo Finance data."""

    @staticmethod
    async def get_stock_info(symbol: str) -> dict[str, Any]:
        """Get comprehensive stock information dict.

        Returns 100+ fields including name, sector, market cap, ratios, etc.
        """
        cache_key = f"info_{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get("trailingPegRatio") is None and not info.get("longName"):
                # Likely invalid symbol — info dict is mostly empty
                # Try one more check
                if not info.get("shortName") and not info.get("longName"):
                    raise InvalidSymbolError(symbol)

            await cache.set(cache_key, info, ttl_seconds=settings.CACHE_TTL_SECONDS)
            return info
        except InvalidSymbolError:
            raise
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch data for {symbol}: {str(e)}")

    @staticmethod
    async def get_historical_data(
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> list[dict[str, Any]]:
        """Get historical OHLCV data as a list of dicts for JSON serialization."""
        cache_key = f"history_{symbol}_{period}_{interval}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, auto_adjust=False)

            if df.empty:
                raise InvalidSymbolError(symbol)

            df = df.reset_index()
            if "Date" in df.columns:
                df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            elif "Datetime" in df.columns:
                df["Date"] = df["Datetime"].dt.strftime("%Y-%m-%d %H:%M")

            # Rename columns to standardized names
            col_map = {
                "Date": "date",
                "Datetime": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
            data = df.rename(columns=col_map).to_dict(orient="records")

            await cache.set(cache_key, data, ttl_seconds=settings.CACHE_TTL_SECONDS)
            return data
        except InvalidSymbolError:
            raise
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch history for {symbol}: {str(e)}")

    @staticmethod
    async def get_news(symbol: str, count: int = 10) -> list[dict[str, Any]]:
        """Get recent news articles for a stock symbol."""
        cache_key = f"news_{symbol}_{count}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:count] if ticker.news else []

            articles = []
            for n in news:
                pub_time = n.get("providerPublishTime", 0)
                articles.append(
                    {
                        "title": n.get("title", ""),
                        "publisher": n.get("publisher", ""),
                        "link": n.get("link", ""),
                        "published": (
                            datetime.fromtimestamp(pub_time).isoformat()
                            if pub_time
                            else ""
                        ),
                        "summary": n.get("summary", ""),
                        "type": n.get("type", ""),
                    }
                )

            await cache.set(cache_key, articles, ttl_seconds=600)  # 10 min TTL for news
            return articles
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch news for {symbol}: {str(e)}")

    @staticmethod
    async def get_financials(symbol: str) -> dict[str, Any]:
        """Get financial statements (income, balance sheet, cash flow)."""
        cache_key = f"financials_{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            ticker = yf.Ticker(symbol)

            def _fetch():
                return {
                    "income_stmt": ticker.financials.to_dict() if ticker.financials is not None else {},
                    "balance_sheet": ticker.balance_sheet.to_dict() if ticker.balance_sheet is not None else {},
                    "cash_flow": ticker.cashflow.to_dict() if ticker.cashflow is not None else {},
                    "quarterly_income": ticker.quarterly_financials.to_dict() if ticker.quarterly_financials is not None else {},
                }

            result = await asyncio.to_thread(_fetch)
            await cache.set(cache_key, result, ttl_seconds=settings.CACHE_TTL_SECONDS)
            return result
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch financials for {symbol}: {str(e)}")

    @staticmethod
    async def search_ticker(query: str, limit: int = 10) -> list[dict[str, str]]:
        """Search for ticker symbols by company name or ticker."""
        cache_key = f"search_{query.lower()}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            # yfinance doesn't have a direct search API, so we try direct lookup first
            # and return a basic result
            results = []

            # Try exact ticker match first
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info
                if info and (info.get("longName") or info.get("shortName")):
                    results.append(
                        {
                            "symbol": query.upper(),
                            "name": info.get("longName") or info.get("shortName", ""),
                            "exchange": info.get("exchange", ""),
                            "type": "stock",
                        }
                    )
            except Exception:
                pass

            # For more results, try common variations
            if len(results) < limit:
                try:
                    # Try with .NS (NSE India) and other common suffixes
                    # This is a simplified search that works for major US stocks
                    common_symbols = [
                        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA",
                        "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "BAC",
                        "DIS", "ADBE", "NFLX", "CRM", "AMD", "INTC", "QCOM", "TXN",
                    ]
                    for sym in common_symbols:
                        if query.upper() in sym and len(results) < limit:
                            try:
                                t = yf.Ticker(sym)
                                inf = t.info
                                name = inf.get("longName") or inf.get("shortName", "")
                                if name and sym not in [r["symbol"] for r in results]:
                                    results.append(
                                        {
                                            "symbol": sym,
                                            "name": name,
                                            "exchange": inf.get("exchange", ""),
                                            "type": "stock",
                                        }
                                    )
                            except Exception:
                                pass
                except Exception:
                    pass

            await cache.set(cache_key, results, ttl_seconds=3600)  # 1 hour for search
            return results[:limit]
        except Exception as e:
            raise DataUnavailableError(f"Search failed: {str(e)}")

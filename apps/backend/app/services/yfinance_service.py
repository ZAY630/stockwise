"""Yahoo Finance data service using yfinance library.

This is the primary data source for StockWise. It requires no API key
and provides price data, fundamentals, news, and more.

Includes static fallback data for when Yahoo Finance is rate-limited,
so the application remains functional even during outages.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any

import yfinance as yf

from app.config import settings
from app.market_config import get_market
from app.middleware.error_handler import DataUnavailableError, InvalidSymbolError
from app.services.cache_service import cache


class RateLimiter:
    """Simple async rate limiter to space out API calls."""

    def __init__(self, min_interval: float):
        self._min_interval = min_interval
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Wait until the minimum interval has passed since the last call."""
        async with self._lock:
            now = time.monotonic()
            wait = self._min_interval - (now - self._last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()


# Global rate limiter instance
_rate_limiter = RateLimiter(settings.YFINANCE_RATE_LIMIT)

# ── Market-aware fallback helpers ────────────────────────────────────

def _get_all_fallback_prices() -> dict[str, dict[str, Any]]:
    """Merge fallback prices from all markets."""
    merged = {}
    for mkt in ["us", "cn"]:
        cfg = get_market(mkt)
        merged.update(cfg.fallback_prices)
    return merged

def _get_all_fallback_info() -> dict[str, dict[str, Any]]:
    """Merge fallback info from all markets."""
    merged = {}
    for mkt in ["us", "cn"]:
        cfg = get_market(mkt)
        merged.update(cfg.fallback_info)
    return merged


def _is_known_symbol(symbol: str) -> bool:
    """Check if we have fallback data for this symbol."""
    return symbol.upper() in _get_all_fallback_prices()


def _is_cn_a_share(symbol: str) -> bool:
    """Check if a symbol looks like a Chinese A-share (6 digits + optional .SS/.SZ)."""
    code = symbol.upper().replace(".SS", "").replace(".SZ", "")
    return code.isdigit() and len(code) == 6


def _generate_fallback_price(symbol: str) -> dict[str, Any]:
    """Generate a reasonable fallback price for any stock code."""
    import hashlib
    # Derive a stable "price" from the symbol so it's consistent per symbol
    h = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    base_price = 10 + (h % 500) + (h % 100) / 100.0  # Range ~10-510
    return {
        "lastPrice": round(base_price, 2),
        "regularMarketPreviousClose": round(base_price * 0.995, 2),
        "open": round(base_price * 0.997, 2),
        "dayHigh": round(base_price * 1.02, 2),
        "dayLow": round(base_price * 0.98, 2),
        "lastVolume": 5_000_000 + (h % 50_000_000),
        "yearHigh": round(base_price * 1.3, 2),
        "yearLow": round(base_price * 0.7, 2),
    }


def _generate_fallback_info(symbol: str) -> dict[str, Any]:
    """Generate basic info for any stock code."""
    code = symbol.upper().replace(".SS", "").replace(".SZ", "")
    return {
        "longName": f"股票 {code}",
        "sector": "未知行业",
        "industry": "未知",
        "marketCap": 10_000_000_000,
        "website": "",
        "longBusinessSummary": f"该公司在{symbol}交易所上市。此数据为系统生成的占位信息，非真实数据。",
    }


class YFinanceService:
    """Wrapper around yfinance for async, cached access to Yahoo Finance data."""

    # ── Stock Info ──────────────────────────────────────────────────

    @staticmethod
    async def get_stock_info(symbol: str) -> dict[str, Any]:
        """Get comprehensive stock information (name, sector, market cap, etc.).

        For CN A-shares, tries Sina Finance first (real-time), then yfinance, then fallback.
        """
        sym = symbol.upper()
        cache_key = f"info_{sym}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # For CN A-shares: try Sina Finance first for real-time price data
        if _is_cn_a_share(sym):
            try:
                from app.services.sina_service import SinaFinanceService
                sina_price = await SinaFinanceService.get_price(sym)
                if sina_price and sina_price.get("lastPrice"):
                    # Merge Sina price into info
                    fb_info = _get_all_fallback_info().get(sym) or _generate_fallback_info(sym)
                    fb_info["currentPrice"] = sina_price.get("lastPrice", 0)
                    fb_info["regularMarketPrice"] = sina_price.get("lastPrice", 0)
                    fb_info["regularMarketPreviousClose"] = sina_price.get("regularMarketPreviousClose", 0)
                    fb_info["regularMarketOpen"] = sina_price.get("open", 0)
                    fb_info["regularMarketDayHigh"] = sina_price.get("dayHigh", 0)
                    fb_info["regularMarketDayLow"] = sina_price.get("dayLow", 0)
                    fb_info["regularMarketVolume"] = sina_price.get("lastVolume", 0)
                    await cache.set(cache_key, fb_info, ttl_seconds=settings.CACHE_TTL_SECONDS)
                    return fb_info
            except Exception:
                pass

        # Try yfinance live API
        try:
            await _rate_limiter.acquire()
            ticker = yf.Ticker(sym)
            info = ticker.info
            if info and (info.get("longName") or info.get("shortName")):
                await cache.set(cache_key, info, ttl_seconds=settings.CACHE_TTL_SECONDS)
                return info
        except Exception:
            pass

        # Fallback: known stock info (merge with price data for consistency)
        fb = _get_all_fallback_info().get(sym)
        if fb:
            fb_price = _get_all_fallback_prices().get(sym, {})
            if "currentPrice" not in fb and fb_price:
                fb["currentPrice"] = fb_price.get("lastPrice", 0)
                fb["regularMarketPrice"] = fb_price.get("lastPrice", 0)
                fb["regularMarketPreviousClose"] = fb_price.get("regularMarketPreviousClose", 0)
            await cache.set(cache_key, fb, ttl_seconds=600)
            return fb

        # Fallback: generate for any CN A-share
        if _is_cn_a_share(sym):
            fb_info = _generate_fallback_info(sym)
            fb_price = _get_all_fallback_prices().get(sym) or _generate_fallback_price(sym)
            # Merge price data into info so get_stock_price tool returns consistent values
            fb_info["currentPrice"] = fb_price.get("lastPrice", 0)
            fb_info["regularMarketPrice"] = fb_price.get("lastPrice", 0)
            fb_info["regularMarketPreviousClose"] = fb_price.get("regularMarketPreviousClose", 0)
            await cache.set(cache_key, fb_info, ttl_seconds=600)
            return fb_info

        raise DataUnavailableError(f"No data available for {sym}")

    # ── Price (fast_info) ───────────────────────────────────────────

    @staticmethod
    async def get_fast_info(symbol: str) -> dict[str, Any]:
        """Get lightweight price data. Sina → yfinance → fallback."""
        sym = symbol.upper()
        cache_key = f"fastinfo_{sym}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # For CN A-shares, try Sina Finance first (real-time, free)
        if _is_cn_a_share(sym):
            try:
                from app.services.sina_service import SinaFinanceService
                result = await SinaFinanceService.get_price(sym)
                if result and result.get("lastPrice"):
                    await cache.set(cache_key, result, ttl_seconds=settings.CACHE_TTL_SECONDS)
                    return result
            except Exception:
                pass

        # Try yfinance live API
        try:
            await _rate_limiter.acquire()
            ticker = yf.Ticker(sym)
            fi = ticker.fast_info
            result = dict(fi) if fi else {}
            if result:
                await cache.set(cache_key, result, ttl_seconds=settings.CACHE_TTL_SECONDS)
                return result
        except Exception:
            pass

        # Fallback: known stock data
        fb = _get_all_fallback_prices().get(sym)
        if fb:
            await cache.set(cache_key, fb, ttl_seconds=120)
            return fb

        # Fallback: generate for any CN A-share
        if _is_cn_a_share(sym):
            fb = _generate_fallback_price(sym)
            await cache.set(cache_key, fb, ttl_seconds=120)
            return fb

        raise DataUnavailableError(f"No price data for {sym}")

    # ── Historical Data ─────────────────────────────────────────────

    @staticmethod
    async def get_historical_data(
        symbol: str, period: str = "1y", interval: str = "1d",
    ) -> list[dict[str, Any]]:
        """Get historical OHLCV data."""
        sym = symbol.upper()
        cache_key = f"history_{sym}_{period}_{interval}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Try live API
        try:
            await _rate_limiter.acquire()
            ticker = yf.Ticker(sym)
            df = ticker.history(period=period, interval=interval, auto_adjust=False)
            if not df.empty:
                df = df.reset_index()
                date_col = "Datetime" if "Datetime" in df.columns else "Date"
                df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")
                col_map = {date_col: "date", "Open": "open", "High": "high",
                           "Low": "low", "Close": "close", "Volume": "volume"}
                data = df.rename(columns=col_map).to_dict(orient="records")
                await cache.set(cache_key, data, ttl_seconds=settings.CACHE_TTL_SECONDS)
                return data
        except Exception:
            pass

        # Fallback: generate synthetic history for any CN A-share or known symbol
        if _is_known_symbol(sym) or _is_cn_a_share(sym):
            # Get base price: try Sina (cached or live), then stored fallback
            base_price = None
            if _is_cn_a_share(sym):
                # Try Sina cache first, then live Sina call
                sina_cached = await cache.get(f"sina_price_{sym}")
                if sina_cached and sina_cached.get("lastPrice"):
                    base_price = sina_cached
                else:
                    try:
                        from app.services.sina_service import SinaFinanceService
                        live = await asyncio.wait_for(
                            SinaFinanceService.get_price(sym), timeout=5.0
                        )
                        if live and live.get("lastPrice"):
                            base_price = live
                    except Exception:
                        pass
            if not base_price:
                base_price = _get_all_fallback_prices().get(sym) or _generate_fallback_price(sym)
            base = base_price.get("lastPrice", 100)
            data = []
            days = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504, "5y": 1260, "max": 1260}
            n = days.get(period, 252)
            for i in range(n, 0, -1):
                d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                import random
                random.seed(f"{sym}{d}")
                # Random daily change: -3% to +3% (realistic)
                daily_change = random.uniform(-0.03, 0.03)
                close_price = base * (1 + random.uniform(-0.15, 0.20))
                open_price = close_price * (1 - daily_change)
                data.append({
                    "date": d,
                    "open": round(open_price, 2),
                    "high": round(max(open_price, close_price) * random.uniform(1.001, 1.015), 2),
                    "low": round(min(open_price, close_price) * random.uniform(0.985, 0.999), 2),
                    "close": round(close_price, 2),
                    "volume": int(base_price.get("lastVolume", 10_000_000) * random.uniform(0.5, 1.5)),
                })
            await cache.set(cache_key, data, ttl_seconds=300)
            return data

        raise DataUnavailableError(f"No history data for {sym}")

    # ── News ────────────────────────────────────────────────────────

    @staticmethod
    async def get_news(symbol: str, count: int = 10) -> list[dict[str, Any]]:
        """Get recent news articles."""
        sym = symbol.upper()
        cache_key = f"news_{sym}_{count}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            await _rate_limiter.acquire()
            ticker = yf.Ticker(sym)
            news_items = ticker.news[:count] if ticker.news else []
            articles = []
            for n in news_items:
                pub_time = n.get("providerPublishTime", 0)
                articles.append({
                    "title": n.get("title", ""),
                    "publisher": n.get("publisher", ""),
                    "link": n.get("link", ""),
                    "published": datetime.fromtimestamp(pub_time).isoformat() if pub_time else "",
                    "summary": n.get("summary", ""),
                    "type": n.get("type", ""),
                })
            await cache.set(cache_key, articles, ttl_seconds=600)
            return articles
        except Exception:
            pass

        # Fallback: return empty list (news is optional)
        return []

    # ── Financials ──────────────────────────────────────────────────

    @staticmethod
    async def get_financials(symbol: str) -> dict[str, Any]:
        """Get financial statements."""
        sym = symbol.upper()
        cache_key = f"financials_{sym}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            await _rate_limiter.acquire()
            ticker = yf.Ticker(sym)
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
        except Exception:
            pass

        # Fallback: empty financials
        return {"income_stmt": {}, "balance_sheet": {}, "cash_flow": {}, "quarterly_income": {}}

    # ── Search ──────────────────────────────────────────────────────

    @staticmethod
    async def search_ticker(query: str, limit: int = 10) -> list[dict[str, str]]:
        """Search for stock symbols by code or company name. Supports US + CN markets."""
        q_raw = query.strip()
        q = q_raw.upper()
        q_lower = q_raw.lower()
        cache_key = f"search_{q}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        results: list[dict[str, str]] = []
        seen: set[str] = set()

        # Helper to add result
        def _add(sym: str, name: str, exchange: str = ""):
            if sym in seen:
                return
            seen.add(sym)
            # Detect exchange for CN stocks
            if not exchange:
                if ".SS" in sym.upper():
                    exchange = "Shanghai"
                elif ".SZ" in sym.upper():
                    exchange = "Shenzhen"
                else:
                    exchange = "NASDAQ" if not sym[0].isdigit() else "Shanghai"
            results.append({"symbol": sym, "name": name, "exchange": exchange, "type": "stock"})

        # 1. Search fallback data (both US + CN) by code or name
        all_info = _get_all_fallback_info()
        for sym, info in all_info.items():
            name = info.get("longName", "")
            # Match: query is in symbol OR query is in name (case-insensitive, partial)
            if q in sym.upper() or q_lower in name.lower() or q_raw in name:
                _add(sym, name)

        # 2. If query looks like a CN stock code (digits), auto-detect suffix and add
        clean_code = q_raw.replace(".SS", "").replace(".SZ", "").strip()
        if clean_code.isdigit() and len(clean_code) == 6:
            from app.market_config import normalize_cn_symbol
            normalized = normalize_cn_symbol(clean_code)
            if normalized not in seen:
                # Check if we have info for it
                info = all_info.get(normalized, {})
                _add(normalized, info.get("longName", f"股票 {clean_code}"))

        # 3. If query is a company name keyword, search across all fallback names
        if len(results) < 3 and len(q_raw) >= 2:
            for sym, info in all_info.items():
                name = info.get("longName", "")
                # Chinese: search individual characters  (e.g., "比亚迪" matches "比亚迪股份有限公司")
                # English: case-insensitive substring
                name_lower = name.lower()
                if q_lower in name_lower or q_raw in name or any(
                    char in name for char in q_raw if ord(char) > 127
                ):
                    if sym not in seen:
                        _add(sym, name)

        # 4. Try live API for US stocks as fallback
        if not results and not q[0].isdigit():
            try:
                await _rate_limiter.acquire()
                ticker = yf.Ticker(q)
                info = ticker.info
                if info and (info.get("longName") or info.get("shortName")):
                    _add(q, info.get("longName") or info.get("shortName", ""),
                          info.get("exchange", ""))
            except Exception:
                pass

        await cache.set(cache_key, results, ttl_seconds=1800)
        return results[:limit]

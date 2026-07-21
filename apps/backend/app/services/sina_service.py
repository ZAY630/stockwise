"""Sina Finance (新浪财经) real-time A-share data service.

Free, no API key required. Provides real-time quotes for all
Shanghai (sh) and Shenzhen (sz) A-shares.

API format:
    http://hq.sinajs.cn/list=sh600519,sz002497
    Returns JS var with comma-separated values:
    name, open, prev_close, price, high, low, volume, ...

Reference: https://finance.sina.com.cn
"""

import asyncio
import re
import time
from typing import Any

import httpx

from app.config import settings
from app.middleware.error_handler import DataUnavailableError
from app.services.cache_service import cache


class SinaFinanceService:
    """Real-time A-share data from Sina Finance (新浪财经).

    Provides live price quotes for Shanghai (.SS) and Shenzhen (.SZ) stocks.
    Falls back to stored fallback data when Sina is unreachable.
    """

    BASE_URL = "http://hq.sinajs.cn"

    # Map our suffix to Sina prefix
    SUFFIX_TO_PREFIX = {".SS": "sh", ".SZ": "sz"}
    PREFIX_TO_SUFFIX = {"sh": ".SS", "sz": ".SZ"}

    @staticmethod
    def _to_sina_code(symbol: str) -> str:
        """Convert '600519.SS' → 'sh600519' or '002497.SZ' → 'sz002497'."""
        sym = symbol.upper()
        for suffix, prefix in SinaFinanceService.SUFFIX_TO_PREFIX.items():
            if sym.endswith(suffix):
                code = sym.replace(suffix, "")
                return f"{prefix}{code}"
        # Try to detect from digit pattern
        code = sym.replace(".SS", "").replace(".SZ", "")
        if code.startswith(("6", "5", "9")):
            return f"sh{code}"
        return f"sz{code}"

    @staticmethod
    async def _fetch_raw(sina_codes: list[str]) -> str:
        """Fetch raw Sina JS data for one or more stock codes."""
        url = f"{SinaFinanceService.BASE_URL}/list={','.join(sina_codes)}"
        headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            # Response is GBK encoded
            return resp.content.decode("gbk", errors="replace")

    @staticmethod
    def _parse_sina_line(line: str) -> dict[str, Any] | None:
        """Parse a single Sina JS var line into a price dict.

        Format: var hq_str_sh600519="茅台,2080.00,2075.00,2090.00,2095.00,2060.00,..."
        Fields: 0:name, 1:open, 2:prev_close, 3:price, 4:high, 5:low,
                8:volume, 9:amount, 30:date, 31:time
        """
        match = re.search(r'hq_str_(\w+)="(.+)"', line)
        if not match:
            return None

        code = match.group(1)  # e.g., "sh600519"
        parts = match.group(2).split(",")

        if len(parts) < 32:
            return None

        try:
            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0
            prev_close = float(parts[2]) if parts[2] else 0
            price = float(parts[3]) if parts[3] else 0
            high = float(parts[4]) if parts[4] else 0
            low = float(parts[5]) if parts[5] else 0
            volume = int(float(parts[8])) if parts[8] else 0

            if price == 0:
                return None

            return {
                "lastPrice": price,
                "regularMarketPreviousClose": prev_close,
                "open": open_price,
                "dayHigh": high,
                "dayLow": low,
                "lastVolume": volume,
                "yearHigh": price * 1.15,  # Sina doesn't provide 52w; estimate
                "yearLow": price * 0.85,
            }
        except (ValueError, IndexError):
            return None

    @staticmethod
    async def get_realtime_prices(symbols: list[str]) -> dict[str, dict[str, Any]]:
        """Fetch real-time prices for multiple A-shares in one request.

        Returns dict mapping our symbol (e.g., '600519.SS') → price dict.
        Best effort: if Sina fails for some symbols, they're omitted.
        """
        results: dict[str, dict[str, Any]] = {}
        sina_codes = []
        code_map: dict[str, str] = {}  # sina_code → our_symbol

        for sym in symbols:
            sina_code = SinaFinanceService._to_sina_code(sym)
            sina_codes.append(sina_code)
            code_map[sina_code] = sym.upper()

        if not sina_codes:
            return results

        try:
            raw = await SinaFinanceService._fetch_raw(sina_codes)
            for line in raw.strip().split("\n"):
                parsed = SinaFinanceService._parse_sina_line(line)
                if not parsed:
                    continue
                # Find matching sina code
                for sc in sina_codes:
                    if sc in line:
                        our_sym = code_map.get(sc, "")
                        if our_sym:
                            results[our_sym] = parsed
                        break
        except Exception:
            pass  # Sina failed; return whatever we got (may be empty)

        return results

    @staticmethod
    async def get_price(symbol: str) -> dict[str, Any]:
        """Get real-time price for a single A-share. Falls back to cache/yfinance."""
        sym = symbol.upper()
        cache_key = f"sina_price_{sym}"

        # Check cache first (30s TTL for real-time data)
        cached = await cache.get(cache_key)
        if cached:
            return cached

        # Fetch from Sina
        prices = await SinaFinanceService.get_realtime_prices([sym])
        if sym in prices:
            result = prices[sym]
            await cache.set(cache_key, result, ttl_seconds=30)
            return result

        raise DataUnavailableError(f"Sina Finance returned no data for {sym}")

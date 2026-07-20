"""Market Data Agent tool implementations."""

import json

from app.services.technical_service import TechnicalService
from app.services.yfinance_service import YFinanceService


async def get_stock_price(symbol: str) -> str:
    """Get latest stock price, daily change, and key stats."""
    info = await YFinanceService.get_stock_info(symbol.upper())

    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("regularMarketPreviousClose", price)
    change = info.get("regularMarketChange", 0)
    change_pct = info.get("regularMarketChangePercent", 0)

    return json.dumps(
        {
            "symbol": symbol.upper(),
            "name": info.get("longName") or info.get("shortName", ""),
            "current_price": price,
            "previous_close": prev_close,
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "day_high": info.get("regularMarketDayHigh", 0),
            "day_low": info.get("regularMarketDayLow", 0),
            "volume": info.get("regularMarketVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "market_cap_formatted": f"${info.get('marketCap', 0) / 1e9:.1f}B",
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            "fifty_two_week_range": f"${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}",
            "beta": info.get("beta", "N/A"),  # Volatility vs market
            "dividend_yield": info.get("dividendYield", 0),
        },
        indent=2,
    )


async def get_historical_prices(
    symbol: str, period: str = "1y", interval: str = "1d"
) -> str:
    """Get historical OHLCV data for chart analysis."""
    data = await YFinanceService.get_historical_data(
        symbol.upper(), period=period, interval=interval
    )

    # Return summary statistics rather than the full dataset
    if not data:
        return json.dumps({"error": "No historical data available"})

    prices = [d.get("close", 0) for d in data if d.get("close")]
    volumes = [d.get("volume", 0) for d in data if d.get("volume")]

    summary = {
        "symbol": symbol.upper(),
        "period": period,
        "interval": interval,
        "data_points": len(data),
        "start_date": data[0].get("date", "") if data else "",
        "end_date": data[-1].get("date", "") if data else "",
        "start_price": prices[0] if prices else 0,
        "end_price": prices[-1] if prices else 0,
        "period_high": max(prices) if prices else 0,
        "period_low": min(prices) if prices else 0,
        "period_change_pct": (
            round(((prices[-1] - prices[0]) / prices[0]) * 100, 2) if prices and prices[0] else 0
        ),
        "average_volume": round(sum(volumes) / len(volumes)) if volumes else 0,
        # Include last 30 data points for short-term pattern recognition
        "recent_data": data[-30:] if len(data) > 30 else data,
    }

    return json.dumps(summary, indent=2)


async def get_technical_indicators(symbol: str, period: str = "1y") -> str:
    """Compute key technical indicators and return with interpretations."""
    history = await YFinanceService.get_historical_data(
        symbol.upper(), period=period, interval="1d"
    )

    indicators = TechnicalService.compute_indicators(history)

    return json.dumps(indicators, indent=2)


async def get_market_context() -> str:
    """Get broader market context: S&P 500, NASDAQ, VIX."""
    try:
        sp500 = await YFinanceService.get_stock_info("^GSPC")
        nasdaq = await YFinanceService.get_stock_info("^IXIC")
        vix = await YFinanceService.get_stock_info("^VIX")

        def _fmt(info):
            price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            change_pct = info.get("regularMarketChangePercent", 0)
            direction = "▲" if change_pct > 0 else "▼" if change_pct < 0 else "—"
            return {
                "price": round(price, 2),
                "change_percent": round(change_pct, 2),
                "direction": direction,
            }

        return json.dumps(
            {
                "sp500": {
                    "name": "S&P 500",
                    **_fmt(sp500),
                    "note": "Tracks 500 large US companies — the main benchmark for the US stock market",
                },
                "nasdaq": {
                    "name": "NASDAQ Composite",
                    **_fmt(nasdaq),
                    "note": "Tech-heavy index — good indicator of technology sector health",
                },
                "vix": {
                    "name": "VIX (Volatility Index)",
                    "price": round(
                        vix.get("currentPrice") or vix.get("regularMarketPrice", 0), 2
                    ),
                    "interpretation": _interpret_vix(
                        vix.get("currentPrice") or vix.get("regularMarketPrice", 0)
                    ),
                    "note": 'The "fear index" — higher values mean more market uncertainty',
                },
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"error": f"Could not fetch market context: {str(e)}"})


def _interpret_vix(vix_price: float) -> str:
    """Interpret the VIX level."""
    if vix_price < 12:
        return f"Very Low ({vix_price}) — market is extremely calm, possibly complacent"
    elif vix_price < 20:
        return f"Normal ({vix_price}) — typical market conditions, no unusual fear"
    elif vix_price < 30:
        return f"Elevated ({vix_price}) — above-average uncertainty, investors are nervous"
    elif vix_price < 40:
        return f"High ({vix_price}) — significant fear, expect large price swings"
    else:
        return f"Extreme ({vix_price}) — panic levels, often associated with market crashes"

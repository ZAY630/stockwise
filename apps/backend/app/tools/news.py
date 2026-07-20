"""News Analysis Agent tool implementations."""

import json

from app.services.news_service import NewsService
from app.services.yfinance_service import YFinanceService


async def fetch_stock_news(symbol: str, count: int = 10) -> str:
    """Fetch recent news articles for a stock."""
    symbol = symbol.upper()
    articles = await NewsService.fetch_news(symbol, count=min(count, 20))

    if not articles:
        company_name = symbol
        try:
            info = await YFinanceService.get_stock_info(symbol)
            company_name = info.get("longName") or info.get("shortName", symbol)
        except Exception:
            pass
        return json.dumps(
            {
                "symbol": symbol,
                "company": company_name,
                "article_count": 0,
                "message": f"No recent news found for {symbol}. This could mean there are no significant news events, or news data is temporarily unavailable.",
            },
            indent=2,
        )

    # Summarize the articles for easier consumption by Claude
    summary = {
        "symbol": symbol,
        "article_count": len(articles),
        "date_range": {
            "oldest": articles[-1].get("published", "") if articles else "",
            "newest": articles[0].get("published", "") if articles else "",
        },
        "articles": articles,
    }

    return json.dumps(summary, indent=2)


async def analyze_headline_sentiment(headline: str, symbol: str) -> str:
    """Analyze sentiment of a headline or article text."""
    sentiment = await NewsService.analyze_sentiment(headline)

    return json.dumps(
        {
            "headline": headline[:200] + ("..." if len(headline) > 200 else ""),
            "symbol": symbol.upper(),
            "sentiment_label": sentiment["sentiment_label"],
            "sentiment_score": sentiment["sentiment_score"],
            "method": sentiment["method"],
            "note": "This is a keyword-based analysis. For nuanced financial news, consider the broader context — a 'loss' headline might actually be positive if the loss was smaller than expected.",
        },
        indent=2,
    )


async def search_sector_news(sector: str, count: int = 5) -> str:
    """Search for broader sector/industry news."""
    sector_lower = sector.lower().strip()

    # Map common sector names to representative ETFs for news lookup
    sector_etfs = {
        "technology": "XLK",
        "healthcare": "XLV",
        "energy": "XLE",
        "financial": "XLF",
        "finance": "XLF",
        "consumer": "XLY",
        "industrial": "XLI",
        "materials": "XLB",
        "real estate": "XLRE",
        "utility": "XLU",
        "utilities": "XLU",
        "communication": "XLC",
    }

    etf = None
    for key, ticker in sector_etfs.items():
        if key in sector_lower:
            etf = ticker
            break

    if etf:
        articles = await NewsService.fetch_news(etf, count=min(count, 10))
    else:
        # Try fetching news for a related keyword via a broad market ETF
        articles = await NewsService.fetch_news("SPY", count=min(count, 10))

    return json.dumps(
        {
            "sector": sector,
            "representative_etf": etf or "SPY (broad market)",
            "article_count": len(articles),
            "articles": articles,
            "note": "Sector news affects all companies in an industry. Consider how these broader trends might impact the specific stock you're analyzing.",
        },
        indent=2,
    )

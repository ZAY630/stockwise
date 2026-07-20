"""News aggregation service.

Aggregates news from multiple sources:
- yfinance (free, built-in)
- Alpha Vantage NEWS_SENTIMENT (requires API key, 25 req/day free)
"""

from typing import Any

from app.config import settings
from app.middleware.error_handler import DataUnavailableError
from app.services.cache_service import cache


class NewsService:
    """Aggregates financial news from multiple sources."""

    @staticmethod
    async def fetch_news(symbol: str, count: int = 10) -> list[dict[str, Any]]:
        """Fetch news articles for a stock from all available sources."""
        cache_key = f"aggregated_news_{symbol}_{count}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        articles: list[dict[str, Any]] = []

        # Source 1: yfinance (always available)
        try:
            from app.services.yfinance_service import YFinanceService

            yf_news = await YFinanceService.get_news(symbol, count)
            for article in yf_news:
                article["source"] = "Yahoo Finance"
            articles.extend(yf_news)
        except Exception:
            pass

        # Source 2: Alpha Vantage (if API key is configured)
        if settings.ALPHA_VANTAGE_API_KEY:
            try:
                import asyncio

                def _fetch_av():
                    import httpx

                    url = "https://www.alphavantage.co/query"
                    params = {
                        "function": "NEWS_SENTIMENT",
                        "tickers": symbol,
                        "apikey": settings.ALPHA_VANTAGE_API_KEY,
                        "limit": min(count, 25),
                    }
                    response = httpx.get(url, params=params, timeout=10)
                    data = response.json()
                    feed = data.get("feed", [])
                    return [
                        {
                            "title": item.get("title", ""),
                            "publisher": ", ".join(item.get("source_domain", [])),
                            "link": item.get("url", ""),
                            "published": item.get("time_published", ""),
                            "summary": item.get("summary", ""),
                            "sentiment_score": item.get("overall_sentiment_score"),
                            "sentiment_label": item.get("overall_sentiment_label"),
                            "source": "Alpha Vantage",
                        }
                        for item in feed[:count]
                    ]

                av_news = await asyncio.to_thread(_fetch_av)
                articles.extend(av_news)
            except Exception:
                pass

        # Deduplicate by title similarity (simple approach: exact title match)
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title = article.get("title", "").strip().lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)

        await cache.set(cache_key, unique_articles[:count], ttl_seconds=600)
        return unique_articles[:count]

    @staticmethod
    async def analyze_sentiment(text: str) -> dict[str, Any]:
        """Analyze sentiment of a text passage.

        Uses lightweight keyword-based analysis as a fallback.
        For deep analysis, the News Agent uses Claude directly.
        """
        positive_words = [
            "beat", "exceed", "growth", "profit", "upgrade", "raise", "outperform",
            "positive", "strong", "record", "surge", "gain", "rally", "bullish",
            "opportunity", "breakthrough", "expansion", "dividend", "buyback",
        ]
        negative_words = [
            "miss", "decline", "loss", "downgrade", "cut", "underperform", "negative",
            "weak", "drop", "plunge", "crash", "bearish", "risk", "lawsuit",
            "investigation", "layoff", "recall", "debt", "bankruptcy", "delisting",
        ]

        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        total = pos_count + neg_count
        if total == 0:
            score = 0.0
            label = "neutral"
        else:
            score = (pos_count - neg_count) / (pos_count + neg_count)
            if score > 0.2:
                label = "positive"
            elif score < -0.2:
                label = "negative"
            else:
                label = "neutral"

        return {
            "sentiment_label": label,
            "sentiment_score": round(score, 3),
            "positive_signals": pos_count,
            "negative_signals": neg_count,
            "method": "keyword_analysis",
            "note": "Lightweight analysis. For deeper analysis, use the News Analysis Agent.",
        }

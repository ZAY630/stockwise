"""Central tool registry — maps tool names to callable implementations.

When Claude requests a tool by name, the BaseAgent looks up the
implementation here and executes it with the provided arguments.
"""

from app.tools.financial import (
    explain_metric,
    get_financial_statements,
    get_key_ratios,
    get_sec_filing,
)
from app.tools.market import (
    get_historical_prices,
    get_market_context,
    get_stock_price,
    get_technical_indicators,
)
from app.tools.news import (
    analyze_headline_sentiment,
    fetch_stock_news,
    search_sector_news,
)
from app.tools.shared import get_company_info

TOOL_REGISTRY: dict[str, callable] = {
    # Financial Agent tools
    "get_financial_statements": get_financial_statements,
    "get_key_ratios": get_key_ratios,
    "get_sec_filing": get_sec_filing,
    "explain_metric": explain_metric,
    # News Agent tools
    "fetch_stock_news": fetch_stock_news,
    "analyze_headline_sentiment": analyze_headline_sentiment,
    "search_sector_news": search_sector_news,
    # Market Agent tools
    "get_stock_price": get_stock_price,
    "get_historical_prices": get_historical_prices,
    "get_technical_indicators": get_technical_indicators,
    "get_market_context": get_market_context,
    # Shared tools
    "get_company_info": get_company_info,
}

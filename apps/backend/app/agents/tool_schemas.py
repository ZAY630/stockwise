"""JSON Schema tool definitions for all agents.

These schemas are passed to the Claude API as tool definitions.
Each tool maps to an implementation in app/tools/.
"""

# ============================================================
# Financial Report Agent Tools
# ============================================================

FINANCIAL_AGENT_TOOLS = [
    {
        "name": "get_financial_statements",
        "description": "Fetch income statement, balance sheet, and cash flow statement for a company. Works for both US stocks (AAPL) and Chinese A-shares (600519.SS, 000858.SZ).",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g., AAPL, TSLA, MSFT",
                },
                "period": {
                    "type": "string",
                    "enum": ["annual", "quarterly"],
                    "default": "annual",
                    "description": "Annual or quarterly statements",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_key_ratios",
        "description": "Calculate and return key financial ratios for a company: P/E, P/B, ROE, ROA, Debt/Equity, Current Ratio, Profit Margin, and others. Includes plain-English explanations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g., AAPL, TSLA",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_sec_filing",
        "description": "Fetch the latest SEC filing (10-K annual report or 10-Q quarterly report) for a company. Can extract specific sections like Risk Factors or Management Discussion & Analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol",
                },
                "filing_type": {
                    "type": "string",
                    "enum": ["10-K", "10-Q"],
                    "default": "10-K",
                    "description": "Type of SEC filing to fetch",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "explain_metric",
        "description": "Look up a beginner-friendly explanation of any financial metric. Use this whenever you introduce a term the user might not know.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric_name": {
                    "type": "string",
                    "description": "Financial metric to explain, e.g., 'EBITDA', 'P/E ratio', 'free cash flow', 'return on equity'",
                },
            },
            "required": ["metric_name"],
        },
    },
]

# ============================================================
# News Analysis Agent Tools
# ============================================================

NEWS_AGENT_TOOLS = [
    {
        "name": "fetch_stock_news",
        "description": "Fetch recent news articles for a stock. Works for US stocks (AAPL, TSLA) and Chinese A-shares (600519, 002497). Returns headlines, summaries, sources, and publication dates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g., AAPL, TSLA",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of articles to fetch (1-20)",
                    "default": 10,
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "analyze_headline_sentiment",
        "description": "Analyze the sentiment (positive/negative/neutral) of a news headline or article text. Returns a sentiment rating with confidence score.",
        "input_schema": {
            "type": "object",
            "properties": {
                "headline": {
                    "type": "string",
                    "description": "The news headline or article text to analyze",
                },
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol for context",
                },
            },
            "required": ["headline", "symbol"],
        },
    },
    {
        "name": "search_sector_news",
        "description": "Search for broader industry/sector news that might affect a company, beyond just ticker-specific headlines.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {
                    "type": "string",
                    "description": "Industry sector, e.g., 'technology', 'healthcare', 'energy', 'finance'",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of articles to fetch",
                    "default": 5,
                },
            },
            "required": ["sector"],
        },
    },
]

# ============================================================
# Market Data Agent Tools
# ============================================================

MARKET_AGENT_TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Get the latest stock price, daily change, day range, 52-week range, volume, and market cap for a stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g., AAPL, TSLA",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_historical_prices",
        "description": "Get historical OHLCV (Open, High, Low, Close, Volume) price data for chart analysis and trend identification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol",
                },
                "period": {
                    "type": "string",
                    "enum": ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    "default": "1y",
                    "description": "How far back to fetch data",
                },
                "interval": {
                    "type": "string",
                    "enum": ["1d", "1wk", "1mo"],
                    "default": "1d",
                    "description": "Data granularity",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_technical_indicators",
        "description": "Compute key technical indicators for a stock: RSI, MACD, SMA (20, 50, 200), Bollinger Bands, ATR, OBV. Returns latest values with plain-English interpretation hints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol",
                },
                "period": {
                    "type": "string",
                    "enum": ["3mo", "6mo", "1y"],
                    "default": "1y",
                    "description": "Data period for indicator calculation (longer = more reliable)",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_market_context",
        "description": "Get broader market context: S&P 500, NASDAQ, and Dow Jones trends, plus VIX (market volatility/fear index). Use this to understand the macro environment before making stock-specific recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

# ============================================================
# Shared Tools (available to all agents)
# ============================================================

SHARED_TOOLS = [
    {
        "name": "get_company_info",
        "description": "Get basic company information: name, sector, industry, description, website, employee count, and headquarters location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g., AAPL, TSLA",
                },
            },
            "required": ["symbol"],
        },
    },
]

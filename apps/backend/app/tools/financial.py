"""Financial Report Agent tool implementations."""

import json

from app.services.edgar_service import EdgarService
from app.services.yfinance_service import YFinanceService


# Built-in glossary for explain_metric
FINANCIAL_GLOSSARY: dict[str, str] = {
    "p/e ratio": "**P/E Ratio (Price-to-Earnings):** Shows how much investors are willing to pay for $1 of company earnings. A high P/E (>25) often means investors expect fast growth. A low P/E (<15) could mean the stock is undervalued — or that the company has problems. Think of it as the 'price tag' on a company's profits.",
    "eps": "**EPS (Earnings Per Share):** The company's profit divided by the number of shares. It's like splitting a pizza — EPS tells you how big each slice is. Higher and growing EPS is generally good.",
    "ebitda": "**EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization):** A measure of a company's operating performance — basically, how much cash the core business generates before accounting for financing decisions, tax environments, and non-cash expenses. Think of it as 'raw operating profit.'",
    "roe": "**ROE (Return on Equity):** Measures how efficiently a company turns investor money into profits. ROE of 15%+ is generally considered good. Think: 'For every $100 investors put in, the company generates $X in profit.'",
    "roa": "**ROA (Return on Assets):** Similar to ROE but uses total assets instead of equity. Shows how well management uses all company resources. Think: 'How much profit does the company squeeze out of everything it owns?'",
    "debt to equity": "**Debt-to-Equity Ratio:** Total debt divided by shareholder equity. Measures financial leverage — how much the company relies on borrowing. A ratio above 2.0 means the company has twice as much debt as equity, which can be risky. Think: 'How much of the company is funded by loans vs. investor money?'",
    "current ratio": "**Current Ratio:** Current assets divided by current liabilities. Measures whether a company can pay its short-term bills. Above 1.5 is generally healthy; below 1.0 is a red flag. Think: 'Can the company pay its bills over the next year?'",
    "free cash flow": "**Free Cash Flow (FCF):** Cash from operations minus capital expenditures. This is the actual cash the company has left after running the business and investing in growth. Think of it as 'disposable income' for the company — can be used for dividends, buybacks, or acquisitions.",
    "profit margin": "**Profit Margin:** Net income divided by revenue. Shows what percentage of each dollar of sales becomes profit. A 20% margin means 20 cents of profit per dollar of sales. Higher is better, but 'good' varies by industry.",
    "p/b ratio": "**P/B Ratio (Price-to-Book):** Stock price divided by book value per share (what the company would be worth if liquidated). Below 1.0 could mean the stock is undervalued. Common for valuing banks and financial companies.",
    "dividend yield": "**Dividend Yield:** Annual dividend per share divided by stock price. Shows what percentage return you get just from dividends. A 3% yield means $3/year for every $100 invested. Think: 'interest rate' on your stock investment.",
    "market cap": "**Market Capitalization:** Total value of all company shares (share price × number of shares). Large-cap (>$10B), mid-cap ($2-10B), small-cap (<$2B). Think: 'What would it cost to buy the entire company?'",
    "beta": "**Beta:** Measures a stock's volatility compared to the overall market (S&P 500). Beta of 1.0 means it moves with the market. Beta of 1.5 means it's 50% more volatile. Beta below 1.0 is less volatile — think 'aggressiveness setting' for a stock.",
    "revenue": "**Revenue (Sales):** The total money a company earns from selling its products/services before any expenses are subtracted. Think of it as the company's 'gross paycheck' — the top line of the income statement.",
    "net income": "**Net Income:** Revenue minus ALL expenses (costs, taxes, interest, depreciation). This is the 'bottom line' — what's left as profit. Think of it as the company's 'take-home pay.'",
    "gross margin": "**Gross Margin:** (Revenue - Cost of Goods Sold) / Revenue. Shows how much profit a company makes after paying direct production costs. 60%+ is excellent for software; 30% might be great for retail. Think: 'How much markup does the company charge above its direct costs?'",
    "operating margin": "**Operating Margin:** Operating income / Revenue. Like gross margin but also subtracts operating expenses (R&D, marketing, admin). Shows how profitable the actual business operations are.",
}


async def get_financial_statements(symbol: str, period: str = "annual") -> str:
    """Fetch financial statements (income, balance sheet, cash flow) for a company."""
    symbol = symbol.upper()

    # Try yfinance first (more reliable for quick data)
    financials = await YFinanceService.get_financials(symbol)

    # Also try EDGAR
    edgar_data = await EdgarService.get_financial_statements(symbol)

    return json.dumps(
        {
            "symbol": symbol,
            "period": period,
            "source_yfinance": {
                "income_statement_available": bool(
                    financials.get("income_stmt")
                ),
                "balance_sheet_available": bool(
                    financials.get("balance_sheet")
                ),
                "cash_flow_available": bool(financials.get("cash_flow")),
                "note": "yfinance provides recent financial data from Yahoo Finance. For detailed SEC filings, use get_sec_filing.",
            },
            "source_edgar": edgar_data,
        },
        indent=2,
    )


async def get_key_ratios(symbol: str) -> str:
    """Calculate and explain key financial ratios for a company."""
    symbol = symbol.upper()
    info = await YFinanceService.get_stock_info(symbol)

    ratios = {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName", "N/A"),
        "valuation_ratios": {
            "pe_ratio": {
                "value": info.get("trailingPE"),
                "explanation": "Price-to-Earnings — how much investors pay per $1 of earnings. S&P 500 average is ~20-25.",
                "assessment": (
                    "Above average — investors expect growth"
                    if info.get("trailingPE", 0) > 25
                    else "Below average — potentially undervalued or facing challenges"
                    if info.get("trailingPE", 0) < 15
                    else "Near market average"
                ),
            },
            "forward_pe": {
                "value": info.get("forwardPE"),
                "explanation": "Forward P/E uses estimated future earnings. Lower than trailing P/E = expected growth.",
            },
            "pb_ratio": {
                "value": info.get("priceToBook"),
                "explanation": "Price-to-Book — stock price vs. liquidation value. Below 1.0 may indicate undervaluation.",
            },
            "peg_ratio": {
                "value": info.get("pegRatio"),
                "explanation": "PEG Ratio — P/E divided by growth rate. Below 1.0 suggests stock may be undervalued relative to growth.",
            },
        },
        "profitability_ratios": {
            "roe": {
                "value": info.get("returnOnEquity"),
                "explanation": "Return on Equity — how efficiently the company turns investor money into profit. 15%+ is strong.",
            },
            "profit_margin": {
                "value": info.get("profitMargins"),
                "explanation": "Net profit margin — what percentage of revenue becomes profit.",
            },
            "operating_margin": {
                "value": info.get("operatingMargins"),
                "explanation": "Operating margin — profit after operating costs but before interest/taxes.",
            },
            "gross_margin": {
                "value": info.get("grossMargins"),
                "explanation": "Gross margin — profit after direct production costs. Higher = stronger pricing power.",
            },
        },
        "financial_health": {
            "debt_to_equity": {
                "value": info.get("debtToEquity"),
                "explanation": "Debt-to-Equity — financial leverage. Above 100% means more debt than equity.",
            },
            "current_ratio": {
                "value": info.get("currentRatio"),
                "explanation": "Current Ratio — ability to pay short-term bills. Above 1.5 is healthy.",
            },
            "quick_ratio": {
                "value": info.get("quickRatio"),
                "explanation": "Quick Ratio — like current ratio but excludes inventory. More conservative.",
            },
        },
        "growth_metrics": {
            "revenue_growth": {
                "value": info.get("revenueGrowth"),
                "explanation": "Year-over-year revenue growth. Positive = growing sales; negative = shrinking.",
            },
            "earnings_growth": {
                "value": info.get("earningsGrowth"),
                "explanation": "Year-over-year earnings growth. More important than revenue growth — shows if profits are growing.",
            },
        },
        "dividends": {
            "dividend_yield": {
                "value": info.get("dividendYield"),
                "explanation": "Annual dividend as percentage of stock price. Mature companies often pay 2-4%.",
            },
            "payout_ratio": {
                "value": info.get("payoutRatio"),
                "explanation": "Percentage of earnings paid as dividends. Below 50% = sustainable; above 80% = could be at risk.",
            },
        },
    }

    return json.dumps(ratios, indent=2)


async def get_sec_filing(symbol: str, filing_type: str = "10-K") -> str:
    """Fetch information about the latest SEC filing for a company."""
    symbol = symbol.upper()
    result = await EdgarService.get_latest_filing(symbol, filing_type)

    return json.dumps(
        {
            "symbol": symbol,
            "filing_type": filing_type,
            "filing_description": (
                "10-K: Annual report — comprehensive overview of business, financials, and risks"
                if filing_type == "10-K"
                else "10-Q: Quarterly report — updated financials and material changes since last 10-K"
            ),
            **result,
        },
        indent=2,
    )


async def explain_metric(metric_name: str) -> str:
    """Look up a beginner-friendly explanation of a financial metric."""
    metric_lower = metric_name.lower().strip()

    # Exact match
    if metric_lower in FINANCIAL_GLOSSARY:
        return FINANCIAL_GLOSSARY[metric_lower]

    # Partial match
    for key, explanation in FINANCIAL_GLOSSARY.items():
        if metric_lower in key or key in metric_lower:
            return explanation

    # Not found — return a generic template
    return (
        f"**{metric_name}:** I don't have a pre-written explanation for this specific metric, "
        "but here's how to think about it: financial metrics generally fall into categories — "
        "valuation (is it cheap or expensive?), profitability (how much profit does it make?), "
        "financial health (can it pay its bills?), or growth (is it expanding?). "
        "Which category do you think this falls into?"
    )

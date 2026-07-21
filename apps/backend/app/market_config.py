"""Market-specific configs for US and China stock markets.

Each market defines: popular tickers, indices, currency, language,
and agent system prompt language override.
"""

from dataclasses import dataclass, field


@dataclass
class MarketConfig:
    """Configuration for a stock market region."""

    code: str  # "us" | "cn"
    name_en: str
    name_native: str
    currency: str
    currency_symbol: str
    locale: str  # "en-US" | "zh-CN"

    # Popular tickers for the dashboard
    popular_tickers: list[str] = field(default_factory=list)
    ticker_names: dict[str, str] = field(default_factory=dict)

    # Market indices for context
    indices: list[str] = field(default_factory=list)
    index_names: dict[str, str] = field(default_factory=dict)

    # Agent prompt language override (appended to system prompt)
    language_instruction: str = ""

    # Fallback prices (approx recent values)
    fallback_prices: dict[str, dict] = field(default_factory=dict)
    fallback_info: dict[str, dict] = field(default_factory=dict)


# ── US Market ──────────────────────────────────────────────────────

US_MARKET = MarketConfig(
    code="us",
    name_en="US Market",
    name_native="US Market",
    currency="USD",
    currency_symbol="$",
    locale="en-US",
    popular_tickers=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"],
    ticker_names={
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "MSFT": "Microsoft Corp.",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "NVDA": "NVIDIA Corp.",
        "META": "Meta Platforms Inc.",
        "NFLX": "Netflix Inc.",
    },
    indices=["^GSPC", "^IXIC", "^VIX"],
    index_names={
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ Composite",
        "^VIX": "VIX (Volatility Index)",
    },
    language_instruction="Respond in English. Use plain, beginner-friendly English.",
    fallback_prices={
        "META": {"lastPrice": 625.00, "regularMarketPreviousClose": 620.50, "open": 622.00,
                 "dayHigh": 630.00, "dayLow": 618.00, "lastVolume": 12000000,
                 "yearHigh": 680.00, "yearLow": 380.00},
        "NFLX": {"lastPrice": 980.00, "regularMarketPreviousClose": 975.00, "open": 977.00,
                 "dayHigh": 990.00, "dayLow": 970.00, "lastVolume": 4500000,
                 "yearHigh": 1050.00, "yearLow": 580.00},
        "AAPL": {"lastPrice": 228.50, "regularMarketPreviousClose": 226.80, "open": 227.10,
                 "dayHigh": 230.20, "dayLow": 226.50, "lastVolume": 48000000,
                 "yearHigh": 260.10, "yearLow": 164.08},
        "GOOGL": {"lastPrice": 192.30, "regularMarketPreviousClose": 190.80, "open": 191.20,
                  "dayHigh": 193.50, "dayLow": 190.10, "lastVolume": 22000000,
                  "yearHigh": 210.90, "yearLow": 128.50},
        "MSFT": {"lastPrice": 445.70, "regularMarketPreviousClose": 442.30, "open": 443.10,
                 "dayHigh": 447.80, "dayLow": 441.50, "lastVolume": 18000000,
                 "yearHigh": 468.35, "yearLow": 340.80},
        "AMZN": {"lastPrice": 222.80, "regularMarketPreviousClose": 220.50, "open": 221.30,
                 "dayHigh": 224.10, "dayLow": 219.80, "lastVolume": 35000000,
                 "yearHigh": 235.50, "yearLow": 150.40},
        "TSLA": {"lastPrice": 248.50, "regularMarketPreviousClose": 252.10, "open": 251.80,
                 "dayHigh": 254.20, "dayLow": 246.30, "lastVolume": 62000000,
                 "yearHigh": 299.29, "yearLow": 138.80},
        "NVDA": {"lastPrice": 135.40, "regularMarketPreviousClose": 133.90, "open": 134.20,
                 "dayHigh": 136.50, "dayLow": 133.10, "lastVolume": 38000000,
                 "yearHigh": 152.89, "yearLow": 60.20},
    },
    fallback_info={
        "META": {"longName": "Meta Platforms Inc.", "sector": "Communication Services", "industry": "Internet Content & Information",
                 "marketCap": 1600000000000, "website": "https://www.meta.com"},
        "NFLX": {"longName": "Netflix Inc.", "sector": "Communication Services", "industry": "Entertainment",
                 "marketCap": 420000000000, "website": "https://www.netflix.com"},
        "AAPL": {"longName": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics",
                 "marketCap": 3500000000000, "website": "https://www.apple.com"},
        "GOOGL": {"longName": "Alphabet Inc.", "sector": "Communication Services", "industry": "Internet Content & Information",
                  "marketCap": 2400000000000, "website": "https://abc.xyz"},
        "MSFT": {"longName": "Microsoft Corporation", "sector": "Technology", "industry": "Software—Infrastructure",
                 "marketCap": 3300000000000, "website": "https://www.microsoft.com"},
        "AMZN": {"longName": "Amazon.com, Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail",
                 "marketCap": 2300000000000, "website": "https://www.amazon.com"},
        "TSLA": {"longName": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers",
                 "marketCap": 800000000000, "website": "https://www.tesla.com"},
        "NVDA": {"longName": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors",
                 "marketCap": 3300000000000, "website": "https://www.nvidia.com"},
    },
)

# ── China Market ───────────────────────────────────────────────────

CN_MARKET = MarketConfig(
    code="cn",
    name_en="China Market",
    name_native="中国A股市场",
    currency="CNY",
    currency_symbol="¥",
    locale="zh-CN",
    # Major A-shares: Shanghai (.SS) and Shenzhen (.SZ)
    popular_tickers=["600519.SS", "000858.SZ", "300750.SZ", "002594.SZ",
                     "601318.SS", "000333.SZ", "002497.SZ", "600887.SS"],
    ticker_names={
        "600519.SS": "贵州茅台 (Moutai)",
        "000858.SZ": "五粮液 (Wuliangye)",
        "300750.SZ": "宁德时代 (CATL)",
        "002594.SZ": "比亚迪 (BYD)",
        "601318.SS": "中国平安 (Ping An)",
        "000333.SZ": "美的集团 (Midea)",
        "002497.SZ": "雅化集团 (Yahua Group)",
        "600887.SS": "伊利股份 (Yili)",
    },
    indices=["000001.SS", "399001.SZ", "399006.SZ"],
    index_names={
        "000001.SS": "上证指数 (Shanghai Composite)",
        "399001.SZ": "深证成指 (Shenzhen Component)",
        "399006.SZ": "创业板指 (ChiNext)",
    },
    language_instruction=(
        "请用中文回答。使用简单易懂的语言，适合投资初学者。"
        "解释术语时请使用生活中常见的比喻。"
    ),
    fallback_prices={
        "600519.SS": {"lastPrice": 1680.00, "regularMarketPreviousClose": 1675.50, "open": 1678.00,
                      "dayHigh": 1690.50, "dayLow": 1672.00, "lastVolume": 3200000,
                      "yearHigh": 1950.00, "yearLow": 1450.00},
        "000858.SZ": {"lastPrice": 152.50, "regularMarketPreviousClose": 151.80, "open": 152.00,
                      "dayHigh": 153.80, "dayLow": 150.90, "lastVolume": 8500000,
                      "yearHigh": 185.00, "yearLow": 128.00},
        "300750.SZ": {"lastPrice": 210.80, "regularMarketPreviousClose": 208.50, "open": 209.00,
                      "dayHigh": 213.20, "dayLow": 207.50, "lastVolume": 12000000,
                      "yearHigh": 280.00, "yearLow": 165.00},
        "000333.SZ": {"lastPrice": 72.30, "regularMarketPreviousClose": 71.90, "open": 72.00,
                      "dayHigh": 73.10, "dayLow": 71.50, "lastVolume": 15000000,
                      "yearHigh": 85.00, "yearLow": 58.00},
        "601398.SS": {"lastPrice": 6.85, "regularMarketPreviousClose": 6.82, "open": 6.83,
                      "dayHigh": 6.92, "dayLow": 6.80, "lastVolume": 45000000,
                      "yearHigh": 7.80, "yearLow": 5.20},
        "600036.SS": {"lastPrice": 42.60, "regularMarketPreviousClose": 42.30, "open": 42.40,
                      "dayHigh": 43.10, "dayLow": 42.10, "lastVolume": 18000000,
                      "yearHigh": 48.50, "yearLow": 35.00},
    },
    fallback_info={
        "600519.SS": {"longName": "贵州茅台酒股份有限公司", "sector": "消费品", "industry": "白酒",
                      "marketCap": 2100000000000, "website": "https://www.moutaichina.com"},
        "000858.SZ": {"longName": "宜宾五粮液股份有限公司", "sector": "消费品", "industry": "白酒",
                      "marketCap": 590000000000, "website": "https://www.wuliangye.com.cn"},
        "300750.SZ": {"longName": "宁德时代新能源科技股份有限公司", "sector": "工业", "industry": "电池制造",
                      "marketCap": 920000000000, "website": "https://www.catl.com"},
        "000333.SZ": {"longName": "美的集团股份有限公司", "sector": "消费品", "industry": "家电制造",
                      "marketCap": 500000000000, "website": "https://www.midea.com"},
        "601398.SS": {"longName": "中国工商银行股份有限公司", "sector": "金融", "industry": "银行",
                      "marketCap": 2400000000000, "website": "https://www.icbc.com.cn"},
        "600036.SS": {"longName": "招商银行股份有限公司", "sector": "金融", "industry": "银行",
                      "marketCap": 1100000000000, "website": "https://www.cmbchina.com"},
    },
)

# ── Chinese A-share suffix auto-detection ──────────────────────────

# Shenzhen stocks: 000xxx, 001xxx, 002xxx, 003xxx, 300xxx, 301xxx
# Shanghai stocks: 600xxx, 601xxx, 603xxx, 605xxx, 688xxx
def normalize_cn_symbol(raw: str) -> str:
    """Auto-detect Chinese A-share exchange suffix from stock code.

    Examples:
        600519 → 600519.SS   (Shanghai)
        000858 → 000858.SZ   (Shenzhen)
        002497 → 002497.SZ   (Shenzhen SME board)
        300750 → 300750.SZ   (Shenzhen ChiNext)
        688xxx → 688xxx.SS   (Shanghai STAR Market)

    Returns the suffix-added symbol, or the original if already has suffix
    or doesn't match any known pattern.
    """
    code = raw.strip().upper()
    # Already has an exchange suffix
    if "." in code:
        return code
    # Must be all digits
    if not code.isdigit() or len(code) != 6:
        return code
    # Shanghai codes: 5xxxxx, 6xxxxx, 9xxxxx (B-shares)
    if code[0] in ("5", "6", "9") and code != "000001":  # 000001.SS is Shanghai Index
        return f"{code}.SS"
    # Shenzhen codes: 0xxxxx, 2xxxxx, 3xxxxx
    if code[0] in ("0", "2", "3"):
        return f"{code}.SZ"
    return code


# ── Extended China fallback data (add more tickers) ─────────────────

CN_MARKET.fallback_prices.update({
    "002497.SZ": {"lastPrice": 16.88, "regularMarketPreviousClose": 16.29, "open": 16.00,
                  "dayHigh": 17.04, "dayLow": 15.87, "lastVolume": 55000000,
                  "yearHigh": 19.40, "yearLow": 14.30},
    "002594.SZ": {"lastPrice": 285.00, "regularMarketPreviousClose": 282.50, "open": 283.00,
                  "dayHigh": 288.50, "dayLow": 281.00, "lastVolume": 8500000,
                  "yearHigh": 320.00, "yearLow": 220.00},
    "300059.SZ": {"lastPrice": 28.50, "regularMarketPreviousClose": 28.10, "open": 28.20,
                  "dayHigh": 29.00, "dayLow": 27.80, "lastVolume": 45000000,
                  "yearHigh": 35.00, "yearLow": 22.00},
    "600887.SS": {"lastPrice": 38.50, "regularMarketPreviousClose": 38.10, "open": 38.20,
                  "dayHigh": 39.00, "dayLow": 37.80, "lastVolume": 18000000,
                  "yearHigh": 45.00, "yearLow": 30.00},
    "601318.SS": {"lastPrice": 52.80, "regularMarketPreviousClose": 52.30, "open": 52.50,
                  "dayHigh": 53.50, "dayLow": 52.00, "lastVolume": 32000000,
                  "yearHigh": 60.00, "yearLow": 42.00},
})

CN_MARKET.fallback_info.update({
    "002497.SZ": {"longName": "四川雅化实业集团股份有限公司", "sector": "工业", "industry": "化工/锂电",
                  "marketCap": 38000000000, "website": "https://www.yahua.cc"},
    "002594.SZ": {"longName": "比亚迪股份有限公司", "sector": "可选消费", "industry": "汽车制造",
                  "marketCap": 820000000000, "website": "https://www.byd.com"},
    "300059.SZ": {"longName": "东方财富信息股份有限公司", "sector": "金融", "industry": "互联网金融",
                  "marketCap": 450000000000, "website": "https://www.eastmoney.com"},
    "600887.SS": {"longName": "内蒙古伊利实业集团股份有限公司", "sector": "消费品", "industry": "乳制品",
                  "marketCap": 240000000000, "website": "https://www.yili.com"},
    "601318.SS": {"longName": "中国平安保险（集团）股份有限公司", "sector": "金融", "industry": "保险",
                  "marketCap": 960000000000, "website": "https://www.pingan.com"},
})

# ── Registry ───────────────────────────────────────────────────────

MARKETS: dict[str, MarketConfig] = {
    "us": US_MARKET,
    "cn": CN_MARKET,
}

DEFAULT_MARKET = "us"


def get_market(market_code: str | None) -> MarketConfig:
    """Get market config by code, falling back to US if invalid."""
    if market_code and market_code in MARKETS:
        return MARKETS[market_code]
    return US_MARKET

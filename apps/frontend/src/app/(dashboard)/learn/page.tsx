"use client";

import { useState } from "react";
import { Search, BookOpen, TrendingUp, BarChart3, DollarSign } from "lucide-react";

const GLOSSARY: Record<string, { term: string; definition: string; category: string }> = {
  "p/e ratio": {
    term: "P/E Ratio (Price-to-Earnings)",
    definition:
      "Shows how much investors pay for $1 of company earnings. A high P/E (>25) often means investors expect fast growth. A low P/E (<15) could mean the stock is undervalued — or that the company has problems. S&P 500 average is ~20-25.",
    category: "Valuation",
  },
  eps: {
    term: "EPS (Earnings Per Share)",
    definition:
      "The company's profit divided by total shares. Higher and growing EPS is generally good — it means each share you own represents more profit.",
    category: "Fundamentals",
  },
  rsi: {
    term: "RSI (Relative Strength Index)",
    definition:
      "A 0-100 momentum indicator. Above 70 = 'overbought' (may drop). Below 30 = 'oversold' (may rise). RSI around 50 means neutral momentum.",
    category: "Technical",
  },
  macd: {
    term: "MACD (Moving Average Convergence Divergence)",
    definition:
      "A trend-following indicator. When the MACD line crosses above the signal line, it's a bullish signal. When it crosses below, it's bearish.",
    category: "Technical",
  },
  "moving average": {
    term: "Moving Average (SMA)",
    definition:
      "The average price over a time window (20, 50, or 200 days are common). When the price is above the moving average, the trend is generally up. The 50-day and 200-day SMAs are the most watched.",
    category: "Technical",
  },
  "market cap": {
    term: "Market Capitalization",
    definition:
      "Total value of all company shares (share price × total shares). Large-cap (>$10B) are stable giants. Mid-cap ($2-10B) are growing companies. Small-cap (<$2B) are riskier with more growth potential.",
    category: "Fundamentals",
  },
  dividend: {
    term: "Dividend & Dividend Yield",
    definition:
      "A dividend is cash paid to shareholders from company profits. Dividend yield = annual dividend ÷ stock price. A 3% yield means $3/year per $100 invested. Mature, stable companies often pay dividends.",
    category: "Income",
  },
  "bull market": {
    term: "Bull Market",
    definition:
      "A prolonged period of rising stock prices (typically +20% or more from recent lows). Bull markets are driven by optimism, economic growth, and investor confidence.",
    category: "Market Concepts",
  },
  "bear market": {
    term: "Bear Market",
    definition:
      "A prolonged period of falling stock prices (typically -20% or more from recent highs). Bear markets are driven by pessimism, economic slowdown, or fear.",
    category: "Market Concepts",
  },
  diversification: {
    term: "Diversification",
    definition:
      "Spreading investments across different stocks, sectors, and asset types to reduce risk. 'Don't put all your eggs in one basket.' A diversified portfolio is less vulnerable to any single company's problems.",
    category: "Strategy",
  },
  "dollar cost averaging": {
    term: "Dollar-Cost Averaging (DCA)",
    definition:
      "Investing a fixed amount regularly regardless of price. When prices are low, you buy more shares; when high, fewer. This reduces the impact of market timing and is recommended for beginners.",
    category: "Strategy",
  },
  etf: {
    term: "ETF (Exchange-Traded Fund)",
    definition:
      "A basket of stocks you can buy like a single stock. ETFs provide instant diversification. Popular examples: SPY (S&P 500), QQQ (NASDAQ 100). Often recommended for beginners.",
    category: "Instruments",
  },
  "support and resistance": {
    term: "Support & Resistance",
    definition:
      "Support = a price level where buying interest tends to stop a decline (a 'floor'). Resistance = a price level where selling pressure tends to stop a rise (a 'ceiling'). These are key levels traders watch.",
    category: "Technical",
  },
  "volume": {
    term: "Trading Volume",
    definition:
      "The number of shares traded in a period. High volume confirms a price move (lots of participants agree). Low volume suggests weak conviction.Volume often spikes during news or earnings.",
    category: "Technical",
  },
  beta: {
    term: "Beta",
    definition:
      "Measures volatility vs. the S&P 500. Beta of 1.0 = moves with the market. Beta of 1.5 = 50% more volatile. Beta below 1.0 = less volatile. Think 'aggressiveness setting' for a stock.",
    category: "Risk",
  },
};

const CATEGORIES = [
  "All",
  "Fundamentals",
  "Technical",
  "Valuation",
  "Income",
  "Risk",
  "Strategy",
  "Market Concepts",
  "Instruments",
];

export default function LearnPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  const entries = Object.entries(GLOSSARY).filter(([key, entry]) => {
    const matchSearch =
      !search ||
      entry.term.toLowerCase().includes(search.toLowerCase()) ||
      entry.definition.toLowerCase().includes(search.toLowerCase()) ||
      key.toLowerCase().includes(search.toLowerCase());
    const matchCategory = category === "All" || entry.category === category;
    return matchSearch && matchCategory;
  });

  return (
    <div className="mx-auto max-w-4xl px-8 py-10">
      <div className="mb-10">
        <h1 className="mb-2 text-3xl font-bold">📚 Learn Investing</h1>
        <p className="text-gray-400">
          Financial concepts explained simply — no jargon, no confusion.
        </p>
      </div>

      {/* Search & filter */}
      <div className="mb-8 space-y-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search for a concept (e.g., P/E ratio, RSI, diversification)..."
            className="w-full rounded-xl border border-gray-700 bg-gray-800/50 py-3 pl-12 pr-4 text-white placeholder-gray-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                category === cat
                  ? "bg-blue-600 text-white"
                  : "border border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-300"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Glossary */}
      <div className="space-y-4">
        {entries.length === 0 && (
          <p className="py-20 text-center text-gray-500">
            No matching concepts found. Try a different search.
          </p>
        )}
        {entries.map(([key, entry]) => (
          <div
            key={key}
            className="rounded-xl border border-gray-800 bg-gray-900/50 p-6"
          >
            <div className="mb-1 flex items-center gap-3">
              <h3 className="text-lg font-semibold">{entry.term}</h3>
              <span className="rounded-full bg-gray-800 px-2.5 py-0.5 text-xs text-gray-500">
                {entry.category}
              </span>
            </div>
            <p className="leading-relaxed text-gray-400">{entry.definition}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

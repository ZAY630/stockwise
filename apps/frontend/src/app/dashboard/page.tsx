"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  ArrowRight,
  AlertTriangle,
  Search,
  Sparkles,
  Star,
} from "lucide-react";
import { apiGet } from "@/lib/api-client";
import { formatCurrency, formatChange } from "@/lib/utils";
import { useMarket } from "@/lib/market-context";
import type { PriceData, SearchResult } from "@/types/common";

// Recommended stocks for each market with brief reasons
const RECOMMENDED: Record<string, { symbol: string; reason: string }[]> = {
  us: [
    { symbol: "AAPL", reason: "Strong AI-driven upgrade cycle" },
    { symbol: "NVDA", reason: "Dominant AI chip position" },
  ],
  cn: [
    { symbol: "300750.SZ", reason: "动力电池龙头·新能源赛道" },
    { symbol: "002594.SZ", reason: "新能源汽车全球领先" },
  ],
};

export default function DashboardHome() {
  const { t, market, marketData: mktCfg, currencySymbol } = useMarket();
  const symbols = mktCfg?.popular_tickers ?? [];

  const [prices, setPrices] = useState<Record<string, PriceData | null>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Recommended stock prices
  const [recPrices, setRecPrices] = useState<Record<string, PriceData | null>>({});
  const recs = RECOMMENDED[market] || RECOMMENDED["us"];

  useEffect(() => {
    if (symbols.length === 0) return;
    let cancelled = false;
    setLoading(true);

    async function fetchAll() {
      const results: Record<string, PriceData | null> = {};
      for (const s of symbols) {
        try {
          const d = await apiGet<PriceData>(`/stocks/${encodeURIComponent(s.symbol)}/price`);
          results[s.symbol] = d;
        } catch {
          results[s.symbol] = null;
        }
      }
      if (!cancelled) {
        setPrices(results);
        const allFailed = Object.values(results).every((v) => v === null);
        if (allFailed) {
          setError(market === "cn"
            ? "数据暂时不可用——请稍后再试" : "Stock data temporarily unavailable — Yahoo Finance rate limit.");
        }
        setLoading(false);
      }
    }
    fetchAll();
    return () => { cancelled = true; };
  }, [market, symbols.map((s) => s.symbol).join(",")]);

  // Format a displayed ticker (strip .SS/.SZ suffix for display)
  const displaySymbol = (s: string) => s.replace(/\.(SS|SZ)$/, "");

  // Fetch recommended stock prices
  useEffect(() => {
    recs.forEach((r) => {
      apiGet<PriceData>(`/stocks/${encodeURIComponent(r.symbol)}/price`)
        .then((d) => setRecPrices((prev) => ({ ...prev, [r.symbol]: d })))
        .catch(() => {});
    });
  }, [market]);

  // Search handler (debounced)
  useEffect(() => {
    if (searchQuery.length < 1) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await apiGet<SearchResult[]>(`/stocks/search?q=${encodeURIComponent(searchQuery)}`);
        setSearchResults(res || []);
        setShowResults(true);
      } catch {
        setSearchResults([]);
      }
      setSearching(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  return (
    <div className="mx-auto max-w-6xl px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">{t.market_overview}</h1>
        <p className="text-gray-400">{t.popular_stocks}</p>
      </div>

      {/* Search Bar */}
      <div className="relative mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchResults.length > 0 && setShowResults(true)}
            onBlur={() => setTimeout(() => setShowResults(false), 200)}
            placeholder={market === "cn"
              ? "搜索股票代码或公司名称（如 比亚迪、002497、宁德时代）"
              : "Search by ticker or company name (e.g., AAPL, Tesla, Apple)"}
            className="w-full rounded-xl border border-gray-700 bg-gray-800/50 py-4 pl-12 pr-4 text-sm text-white placeholder-gray-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          />
          {searching && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
            </div>
          )}
        </div>
        {/* Search results dropdown */}
        {showResults && searchResults.length > 0 && (
          <div className="absolute z-20 mt-2 w-full rounded-xl border border-gray-700 bg-gray-900 py-2 shadow-xl">
            {searchResults.map((r) => (
              <Link
                key={r.symbol}
                href={`/dashboard/stock/${encodeURIComponent(r.symbol)}`}
                className="flex items-center justify-between px-4 py-3 transition hover:bg-gray-800/50"
                onClick={() => { setShowResults(false); setSearchQuery(""); }}
              >
                <div>
                  <span className="font-semibold text-white">{displaySymbol(r.symbol)}</span>
                  <span className="ml-2 text-xs text-gray-500">{r.exchange}</span>
                  <p className="text-sm text-gray-400">{r.name}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-gray-600" />
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Today's Recommended Stocks */}
      <div className="mb-8">
        <div className="mb-4 flex items-center gap-2">
          <Star className="h-5 w-5 text-amber-400" />
          <h2 className="text-lg font-semibold text-white">
            {market === "cn" ? "今日推荐" : "Today's Picks"}
          </h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {recs.map((rec) => {
            const price = recPrices[rec.symbol];
            const changeInfo = formatChange(price?.change_percent ?? null);
            return (
              <Link
                key={rec.symbol}
                href={`/dashboard/stock/${encodeURIComponent(rec.symbol)}`}
                className="group rounded-xl border border-amber-500/20 bg-gradient-to-r from-amber-500/5 to-transparent p-5 transition hover:border-amber-500/40"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-amber-400" />
                      <span className="font-bold text-white">{displaySymbol(rec.symbol)}</span>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">{rec.reason}</p>
                  </div>
                  {price && (
                    <div className="text-right">
                      <p className="font-semibold text-white">
                        {currencySymbol}{price.price.toFixed(2)}
                      </p>
                      <p className={`text-xs ${changeInfo.color}`}>{changeInfo.text}</p>
                    </div>
                  )}
                  {!price && (
                    <div className="h-8 w-20 animate-pulse rounded bg-gray-800" />
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Ticker grid header */}

      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 px-5 py-4 text-sm text-amber-300">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <p className="text-amber-400/80">{error}</p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {symbols.map((s) => {
          const data = prices[s.symbol];
          const changeInfo = formatChange(data?.change_percent ?? null);
          const showData = !loading && data;

          return (
            <Link
              key={s.symbol}
              href={`/dashboard/stock/${encodeURIComponent(s.symbol)}`}
              className="group rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50 hover:bg-gray-800/50"
            >
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <span className="text-lg font-bold">{displaySymbol(s.symbol)}</span>
                  <p className="text-xs text-gray-500">{s.name}</p>
                </div>
                {showData && (
                  <span className="text-2xl font-semibold">
                    {currencySymbol}{data.price.toFixed(2)}
                  </span>
                )}
                {loading && (
                  <div className="h-7 w-24 animate-pulse rounded bg-gray-800" />
                )}
                {!loading && !data && (
                  <span className="text-xs text-gray-600">
                    {market === "cn" ? "暂不可用" : "Unavailable"}
                  </span>
                )}
              </div>
              {showData && (
                <div className="flex items-center gap-2">
                  {data.change >= 0 ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={changeInfo.color}>{changeInfo.text}</span>
                </div>
              )}
              <div className="mt-4 flex items-center gap-1 text-sm text-blue-400 opacity-0 transition group-hover:opacity-100">
                {t.view_analysis} <ArrowRight className="h-3 w-3" />
              </div>
            </Link>
          );
        })}
      </div>

      <div className="mt-12 grid gap-4 sm:grid-cols-2">
        <Link href="/dashboard/chat" className="rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50">
          <h3 className="mb-2 text-lg font-semibold">💬 {t.chat_ai}</h3>
          <p className="text-sm text-gray-400">{t.chat_desc}</p>
        </Link>
        <Link href="/dashboard/learn" className="rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50">
          <h3 className="mb-2 text-lg font-semibold">📚 {t.learn_basics}</h3>
          <p className="text-sm text-gray-400">{t.learn_desc}</p>
        </Link>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { TrendingUp, TrendingDown, ArrowRight, Search } from "lucide-react";
import { apiGet } from "@/lib/api-client";
import { formatCurrency, formatChange } from "@/lib/utils";
import type { PriceData } from "@/types/common";

const POPULAR_TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA"];

export default function DashboardHome() {
  const [marketData, setMarketData] = useState<
    Record<string, PriceData | null>
  >({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all(
      POPULAR_TICKERS.map((sym) =>
        apiGet<PriceData>(`/stocks/${sym}/price`)
          .then((d) => [sym, d] as const)
          .catch(() => [sym, null] as const)
      )
    ).then((results) => {
      setMarketData(Object.fromEntries(results));
      setLoading(false);
    });
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-8 py-10">
      <div className="mb-10">
        <h1 className="mb-2 text-3xl font-bold">Market Overview</h1>
        <p className="text-gray-400">
          Popular stocks — click any to see detailed AI analysis
        </p>
      </div>

      {/* Ticker grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {POPULAR_TICKERS.map((symbol) => {
          const data = marketData[symbol];
          const changeInfo = formatChange(data?.change_percent ?? null);

          return (
            <Link
              key={symbol}
              href={`/dashboard/stock/${symbol}`}
              className="group rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50 hover:bg-gray-800/50"
            >
              <div className="mb-3 flex items-center justify-between">
                <span className="text-lg font-bold">{symbol}</span>
                {!loading && data && (
                  <span className="text-2xl font-semibold">
                    {formatCurrency(data.price)}
                  </span>
                )}
                {loading && (
                  <div className="h-7 w-24 animate-pulse rounded bg-gray-800" />
                )}
              </div>
              {!loading && data && (
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
                View Analysis <ArrowRight className="h-3 w-3" />
              </div>
            </Link>
          );
        })}
      </div>

      {/* Quick actions */}
      <div className="mt-12 grid gap-4 sm:grid-cols-2">
        <Link
          href="/dashboard/chat"
          className="rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50"
        >
          <h3 className="mb-2 text-lg font-semibold">
            💬 Ask the AI Agents
          </h3>
          <p className="text-sm text-gray-400">
            Chat with specialized agents about any stock. Get financial
            analysis, news sentiment, and market recommendations.
          </p>
        </Link>
        <Link
          href="/dashboard/learn"
          className="rounded-xl border border-gray-800 bg-gray-900/50 p-6 transition hover:border-blue-500/50"
        >
          <h3 className="mb-2 text-lg font-semibold">
            📚 Learn Investing Basics
          </h3>
          <p className="text-sm text-gray-400">
            Understand P/E ratios, technical indicators, financial statements,
            and more — explained simply.
          </p>
        </Link>
      </div>
    </div>
  );
}

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  TrendingUp,
  BarChart3,
  Newspaper,
  Sparkles,
  ArrowRight,
  Search,
} from "lucide-react";

export default function LandingPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/dashboard/stock/${searchQuery.trim().toUpperCase()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Hero */}
      <header className="relative overflow-hidden border-b border-gray-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/30 via-gray-950 to-emerald-900/20" />
        <div className="relative mx-auto max-w-6xl px-6 py-24 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300">
            <Sparkles className="h-4 w-4" />
            Powered by Multi-Agent AI
          </div>
          <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-7xl">
            <span className="bg-gradient-to-r from-blue-400 via-white to-emerald-400 bg-clip-text text-transparent">
              StockWise
            </span>
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-lg text-gray-400">
            Learn stock investment with AI agents that analyze financials, news,
            and market data. Built for beginners — every term explained, every
            recommendation reasoned.
          </p>

          {/* Search */}
          <form onSubmit={handleSearch} className="mx-auto max-w-xl">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter a stock ticker (e.g., AAPL, TSLA)..."
                  className="w-full rounded-xl border border-gray-700 bg-gray-800/50 py-4 pl-12 pr-4 text-lg text-white placeholder-gray-500 backdrop-blur transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                />
              </div>
              <button
                type="submit"
                className="rounded-xl bg-blue-600 px-8 py-4 font-semibold text-white transition hover:bg-blue-500"
              >
                Analyze
              </button>
            </div>
          </form>
        </div>
      </header>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-24">
        <h2 className="mb-16 text-center text-3xl font-bold">
          Three AI Agents, One Complete Picture
        </h2>
        <div className="grid gap-8 md:grid-cols-3">
          <FeatureCard
            icon={<Newspaper className="h-8 w-8" />}
            title="News Analysis Agent"
            description="Fetches financial news, analyzes sentiment, and explains how headlines might impact stock prices — with full reasoning chains."
            color="purple"
          />
          <FeatureCard
            icon={<BarChart3 className="h-8 w-8" />}
            title="Financial Report Agent"
            description="Analyzes balance sheets, income statements, and SEC filings. Explains P/E ratios, ROE, and more in plain English with helpful analogies."
            color="blue"
          />
          <FeatureCard
            icon={<TrendingUp className="h-8 w-8" />}
            title="Market Data Agent"
            description="Reads charts, computes RSI/MACD/Bollinger Bands, and generates buy/sell/hold recommendations with specific price levels."
            color="emerald"
          />
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-gray-800">
        <div className="mx-auto max-w-4xl px-6 py-20 text-center">
          <h2 className="mb-4 text-3xl font-bold">Ready to learn investing?</h2>
          <p className="mb-8 text-gray-400">
            No jargon. No confusion. Just clear, educational analysis powered by
            AI.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-8 py-4 font-semibold text-white transition hover:bg-blue-500"
          >
            Open Dashboard <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: "blue" | "purple" | "emerald";
}) {
  const borders = {
    blue: "border-blue-500/30 hover:border-blue-500/60",
    purple: "border-purple-500/30 hover:border-purple-500/60",
    emerald: "border-emerald-500/30 hover:border-emerald-500/60",
  };
  const bgs = {
    blue: "bg-blue-500/10",
    purple: "bg-purple-500/10",
    emerald: "bg-emerald-500/10",
  };
  const texts = {
    blue: "text-blue-400",
    purple: "text-purple-400",
    emerald: "text-emerald-400",
  };

  return (
    <div
      className={`rounded-2xl border ${borders[color]} bg-gray-800/30 p-8 backdrop-blur transition`}
    >
      <div
        className={`mb-4 inline-flex rounded-xl ${bgs[color]} p-3 ${texts[color]}`}
      >
        {icon}
      </div>
      <h3 className="mb-3 text-xl font-semibold">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Newspaper,
  Sparkles,
  Loader2,
} from "lucide-react";
import { apiGet, apiPost } from "@/lib/api-client";
import { formatCurrency, formatChange, formatLargeNumber } from "@/lib/utils";
import type {
  PriceData,
  StockInfo,
  AnalysisResponse,
  OHLCVPoint,
} from "@/types/common";

export default function StockDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const ticker = symbol.toUpperCase();

  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [priceLoading, setPriceLoading] = useState(true);

  const [activeTab, setActiveTab] = useState<
    "market" | "financial" | "news" | "comprehensive"
  >("comprehensive");
  const [analysis, setAnalysis] = useState<string>("");
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisDone, setAnalysisDone] = useState(false);

  // Fetch price and company info
  useEffect(() => {
    setPriceLoading(true);
    Promise.all([
      apiGet<PriceData>(`/stocks/${ticker}/price`).catch(() => null),
      apiGet<StockInfo>(`/stocks/${ticker}`).catch(() => null),
    ]).then(([price, info]) => {
      setPriceData(price);
      setStockInfo(info);
      setPriceLoading(false);
    });
  }, [ticker]);

  // Fetch analysis when tab changes
  useEffect(() => {
    setAnalysisLoading(true);
    setAnalysisDone(false);
    setAnalysis("");

    let endpoint = "";
    switch (activeTab) {
      case "market":
        endpoint = "/analysis/market";
        break;
      case "financial":
        endpoint = "/analysis/financial";
        break;
      case "news":
        endpoint = "/analysis/news";
        break;
      case "comprehensive":
        endpoint = "/analysis/comprehensive";
        break;
    }

    apiPost<AnalysisResponse>(endpoint, {
      symbol: ticker,
      question:
        activeTab === "comprehensive"
          ? `Give me a comprehensive analysis of ${ticker}. Should I invest?`
          : undefined,
    })
      .then((res) => {
        setAnalysis(res.analysis);
        setAnalysisDone(true);
      })
      .catch((err) => {
        setAnalysis(`Error: ${err.message}`);
        setAnalysisDone(true);
      })
      .finally(() => setAnalysisLoading(false));
  }, [ticker, activeTab]);

  const changeInfo = formatChange(priceData?.change_percent ?? null);

  return (
    <div className="mx-auto max-w-5xl px-8 py-10">
      {/* Header */}
      <div className="mb-10">
        {priceLoading ? (
          <div className="space-y-3">
            <div className="h-8 w-48 animate-pulse rounded bg-gray-800" />
            <div className="h-6 w-32 animate-pulse rounded bg-gray-800" />
          </div>
        ) : (
          <>
            <h1 className="mb-1 text-3xl font-bold">
              {ticker}{" "}
              <span className="text-xl font-normal text-gray-400">
                {stockInfo?.name || ""}
              </span>
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold">
                {formatCurrency(priceData?.price)}
              </span>
              {priceData && (
                <span
                  className={`flex items-center gap-1 text-lg font-semibold ${changeInfo.color}`}
                >
                  {priceData.change_percent >= 0 ? (
                    <TrendingUp className="h-5 w-5" />
                  ) : (
                    <TrendingDown className="h-5 w-5" />
                  )}
                  {changeInfo.text}
                </span>
              )}
            </div>
            {stockInfo && (
              <p className="mt-2 text-sm text-gray-500">
                {stockInfo.sector} | {stockInfo.industry} | Market Cap:{" "}
                {formatLargeNumber(stockInfo.market_cap)}
              </p>
            )}
          </>
        )}
      </div>

      {/* Analysis Tabs */}
      <div className="mb-8 flex gap-2 border-b border-gray-800">
        {[
          { key: "comprehensive", label: "Full Analysis", icon: Sparkles },
          { key: "market", label: "Market Data", icon: TrendingUp },
          { key: "financial", label: "Financials", icon: BarChart3 },
          { key: "news", label: "News", icon: Newspaper },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() =>
              setActiveTab(
                tab.key as "comprehensive" | "market" | "financial" | "news"
              )
            }
            className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition ${
              activeTab === tab.key
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Analysis Content */}
      <div className="min-h-[400px] rounded-xl border border-gray-800 bg-gray-900/50 p-8">
        {analysisLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="mb-4 h-8 w-8 animate-spin text-blue-400" />
            <p className="text-gray-400">
              {activeTab === "comprehensive"
                ? "All three agents are analyzing this stock..."
                : "Agent is analyzing..."}
            </p>
            <p className="mt-1 text-sm text-gray-600">
              This may take 10-30 seconds
            </p>
          </div>
        ) : (
          <div className="prose prose-invert max-w-none">
            {analysis
              .split("\n")
              .filter((line) => line.trim())
              .map((line, i) => {
                // Render markdown-like formatting
                if (line.startsWith("# ")) {
                  return (
                    <h1
                      key={i}
                      className="mb-4 mt-6 text-2xl font-bold first:mt-0"
                    >
                      {line.slice(2)}
                    </h1>
                  );
                }
                if (line.startsWith("## ")) {
                  return (
                    <h2
                      key={i}
                      className="mb-3 mt-6 text-xl font-semibold text-blue-400"
                    >
                      {line.slice(3)}
                    </h2>
                  );
                }
                if (line.startsWith("### ")) {
                  return (
                    <h3
                      key={i}
                      className="mb-2 mt-4 text-lg font-semibold"
                    >
                      {line.slice(4)}
                    </h3>
                  );
                }
                if (line.startsWith("- ")) {
                  return (
                    <li key={i} className="ml-4 text-gray-300">
                      {line.slice(2)}
                    </li>
                  );
                }
                if (line.startsWith("> ")) {
                  return (
                    <blockquote
                      key={i}
                      className="my-3 border-l-4 border-blue-500/50 pl-4 italic text-gray-400"
                    >
                      {line.slice(2)}
                    </blockquote>
                  );
                }
                if (line.startsWith("**") && line.includes(":**")) {
                  const [label, ...rest] = line.split(":**");
                  return (
                    <p key={i} className="mb-2">
                      <strong className="text-white">
                        {label.replace("**", "")}:
                      </strong>
                      {rest.join(":**")}
                    </p>
                  );
                }
                if (line.startsWith("**") && line.endsWith("**")) {
                  return (
                    <p
                      key={i}
                      className="mb-2 font-bold text-white"
                    >
                      {line.slice(2, -2)}
                    </p>
                  );
                }
                return (
                  <p key={i} className="mb-2 text-gray-300">
                    {line}
                  </p>
                );
              })}
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <p className="mt-6 text-xs text-gray-600">
        ⚠️ This analysis is for educational purposes only. It is not financial
        advice. All investments carry risk. Past performance does not guarantee
        future results.
      </p>
    </div>
  );
}

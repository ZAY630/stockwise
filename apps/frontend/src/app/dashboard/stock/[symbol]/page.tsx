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
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import StockChart from "@/components/StockChart";
import { apiGet, apiPost } from "@/lib/api-client";
import { formatCurrency, formatChange, formatLargeNumber } from "@/lib/utils";
import { useMarket } from "@/lib/market-context";
import type {
  PriceData,
  StockInfo,
  AnalysisResponse,
  OHLCVPoint,
} from "@/types/common";

const displaySymbol = (s: string) => s.replace(/\.(SS|SZ)$/, "");

export default function StockDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const ticker = decodeURIComponent(symbol).toUpperCase();
  const { t, market, currencySymbol, locale } = useMarket();

  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [priceLoading, setPriceLoading] = useState(true);

  const [activeTab, setActiveTab] = useState<
    "market" | "financial" | "news" | "comprehensive" | null
  >(null); // Don't auto-load — wait for user to pick a tab
  const [analysis, setAnalysis] = useState<string>("");
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [loadedTabs, setLoadedTabs] = useState<Set<string>>(new Set());

  // Fetch price and company info (fast — uses cache/fallback)
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

  // Fetch analysis only when user clicks a tab (not on page load)
  const loadAnalysis = (tab: "market" | "financial" | "news" | "comprehensive") => {
    setActiveTab(tab);
    if (loadedTabs.has(tab)) return; // Already loaded — cached in state
    setLoadedTabs((prev) => new Set(prev).add(tab));

    setAnalysisLoading(true);
    setAnalysis("");

    const endpoint =
      tab === "market" ? "/analysis/market" :
      tab === "financial" ? "/analysis/financial" :
      tab === "news" ? "/analysis/news" :
      "/analysis/comprehensive";

    apiPost<AnalysisResponse>(endpoint, {
      symbol: ticker,
      market: market,
      question:
        tab === "comprehensive"
          ? `Give me a comprehensive analysis of ${ticker}. Should I invest?`
          : undefined,
    })
      .then((res) => {
        setAnalysis(res.analysis);
        setAnalysisLoading(false);
      })
      .catch((err) => {
        setAnalysis(`**Error:** ${err.message}`);
        setAnalysisLoading(false);
      });
  };

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

      {/* Price Chart */}
      <div className="mb-8">
        <StockChart symbol={ticker} />
      </div>

      {/* Analysis Tabs */}
      <div className="mb-8 flex gap-2 border-b border-gray-800">
        {[
          { key: "comprehensive", label: t.full_analysis, icon: Sparkles },
          { key: "market", label: t.market_data_tab, icon: TrendingUp },
          { key: "financial", label: t.financials_tab, icon: BarChart3 },
          { key: "news", label: t.news_tab, icon: Newspaper },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() =>
              loadAnalysis(
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
        {!activeTab ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Sparkles className="mb-4 h-12 w-12 text-blue-400" />
            <h3 className="mb-2 text-lg font-semibold text-gray-300">
              {t.ready_analyze} {displaySymbol(ticker)}
            </h3>
            <p className="mb-6 max-w-md text-sm text-gray-500">{t.select_tab}</p>
            <div className="flex gap-3">
              <button
                onClick={() => loadAnalysis("comprehensive")}
                className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-blue-500"
              >
                {t.full_analysis}
              </button>
              <button
                onClick={() => loadAnalysis("market")}
                className="rounded-xl border border-gray-700 px-5 py-2.5 text-sm font-medium text-gray-300 transition hover:border-gray-500"
              >
                {t.quick_market_view}
              </button>
            </div>
          </div>
        ) : analysisLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="mb-4 h-8 w-8 animate-spin text-blue-400" />
            <p className="text-gray-400">
              {activeTab === "comprehensive" ? t.all_agents_analyzing : t.analyzing}
            </p>
            <p className="mt-1 text-sm text-gray-600">{t.cached_notice}</p>
          </div>
        ) : (
          <div className="markdown-content prose prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Tables
                table: ({ children }) => (
                  <div className="my-4 overflow-x-auto rounded-lg border border-gray-700">
                    <table className="min-w-full divide-y divide-gray-700 text-sm">
                      {children}
                    </table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-gray-800/50">{children}</thead>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-3 text-left font-semibold text-blue-300">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-2.5 text-gray-200 border-t border-gray-700/50">
                    {children}
                  </td>
                ),
                tr: ({ children }) => <tr>{children}</tr>,
                // Headings
                h1: ({ children }) => (
                  <h1 className="mb-4 mt-6 text-2xl font-bold first:mt-0 text-white">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="mb-3 mt-6 text-xl font-semibold text-blue-400 border-b border-gray-700/50 pb-2">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="mb-2 mt-4 text-lg font-semibold text-white">
                    {children}
                  </h3>
                ),
                // Lists
                ul: ({ children }) => (
                  <ul className="mb-4 space-y-1 list-disc list-inside text-gray-300">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="mb-4 space-y-1 list-decimal list-inside text-gray-300">
                    {children}
                  </ol>
                ),
                li: ({ children }) => <li className="ml-2">{children}</li>,
                // Paragraphs
                p: ({ children }) => (
                  <p className="mb-3 leading-relaxed text-gray-200">{children}</p>
                ),
                // Links
                a: ({ children, href }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 underline hover:text-blue-300"
                  >
                    {children}
                  </a>
                ),
                // Bold/Strong
                strong: ({ children }) => (
                  <strong className="font-semibold text-white">{children}</strong>
                ),
                // Emphasis
                em: ({ children }) => (
                  <em className="italic text-gray-300">{children}</em>
                ),
                // Code
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="rounded bg-gray-800 px-1.5 py-0.5 text-sm text-blue-300 font-mono">
                      {children}
                    </code>
                  ) : (
                    <pre className="my-3 overflow-x-auto rounded-lg bg-gray-800/70 p-4 text-sm font-mono text-gray-200">
                      <code className={className}>{children}</code>
                    </pre>
                  );
                },
                // Blockquotes
                blockquote: ({ children }) => (
                  <blockquote className="my-4 border-l-4 border-blue-500/50 bg-blue-500/5 pl-4 py-2 italic text-gray-300 rounded-r-lg">
                    {children}
                  </blockquote>
                ),
                // Horizontal rule
                hr: () => <hr className="my-6 border-gray-700" />,
              }}
            >
              {analysis}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <p className="mt-6 text-xs text-gray-600">{t.disclaimer}</p>
    </div>
  );
}

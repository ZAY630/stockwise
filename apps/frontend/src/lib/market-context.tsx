"use client";

import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

export type MarketCode = "us" | "cn";

export interface TickerInfo {
  symbol: string;
  name: string;
}

export interface MarketData {
  code: MarketCode;
  name_en: string;
  name_native: string;
  currency: string;
  currency_symbol: string;
  locale: string;
  popular_tickers: TickerInfo[];
  indices: TickerInfo[];
}

// ── i18n translations ──────────────────────────────────────────────

type TranslationKey =
  | "market_overview" | "popular_stocks" | "view_analysis" | "chat_ai"
  | "chat_desc" | "learn_basics" | "learn_desc" | "full_analysis"
  | "market_data_tab" | "financials_tab" | "news_tab" | "watchlist"
  | "add_watchlist" | "ready_analyze" | "select_tab" | "quick_market_view"
  | "analyzing" | "all_agents_analyzing" | "cached_notice"
  | "agents_thinking" | "ask_investing" | "type_message"
  | "price_chart" | "chart_legend" | "chart_tip" | "disclaimer"
  | "dashboard" | "chat" | "learn" | "overview";

type Translations = Record<TranslationKey, string>;

const US_TRANSLATIONS: Translations = {
  market_overview: "Market Overview",
  popular_stocks: "Popular stocks — click any to see detailed AI analysis",
  view_analysis: "View Analysis",
  chat_ai: "Ask the AI Agents",
  chat_desc: "Chat with specialized agents about any stock. Get financial analysis, news sentiment, and market recommendations.",
  learn_basics: "Learn Investing Basics",
  learn_desc: "Understand P/E ratios, technical indicators, financial statements, and more — explained simply.",
  full_analysis: "Full Analysis",
  market_data_tab: "Market Data",
  financials_tab: "Financials",
  news_tab: "News",
  watchlist: "My Watchlist",
  add_watchlist: "Add stocks above to start tracking them",
  ready_analyze: "Ready to analyze",
  select_tab: "Select a tab above to get AI-powered analysis. Already loaded tabs are cached — switching back is instant.",
  quick_market_view: "Quick Market View",
  analyzing: "Agent is analyzing...",
  all_agents_analyzing: "All three agents are analyzing this stock...",
  cached_notice: "First load ~30-90s, subsequent loads instant (cached)",
  agents_thinking: "Agent is thinking...",
  ask_investing: "Ask anything about investing",
  type_message: "Ask about stocks, investing, or financial concepts...",
  price_chart: "Price Chart",
  chart_legend: "Candlestick + SMA 20 (amber) + SMA 50 (purple)",
  chart_tip: "📖 How to read this: Green candles = price went up, red = down. The wicks (thin lines) show the day's high and low. SMA lines show the average price over time — when the shorter SMA crosses above the longer one, it can signal an uptrend (\"Golden Cross\").",
  disclaimer: "⚠️ This analysis is for educational purposes only. It is not financial advice. All investments carry risk. Past performance does not guarantee future results.",
  dashboard: "Dashboard",
  chat: "Chat",
  learn: "Learn",
  overview: "Overview",
};

const CN_TRANSLATIONS: Translations = {
  market_overview: "市场概览",
  popular_stocks: "热门股票 — 点击任意股票查看AI详细分析",
  view_analysis: "查看分析",
  chat_ai: "AI 智能体对话",
  chat_desc: "与专业智能体讨论任何股票。获取财务分析、新闻情绪和市场建议。",
  learn_basics: "学习投资基础",
  learn_desc: "了解市盈率、技术指标、财务报表等 — 用通俗语言解释。",
  full_analysis: "综合分析",
  market_data_tab: "市场数据",
  financials_tab: "财务分析",
  news_tab: "新闻动态",
  watchlist: "我的自选",
  add_watchlist: "在上方添加股票开始跟踪",
  ready_analyze: "准备分析",
  select_tab: "选择上方标签获取AI分析。已加载的标签已缓存 — 切换即时显示。",
  quick_market_view: "快速市场查看",
  analyzing: "智能体正在分析...",
  all_agents_analyzing: "三个智能体正在同时分析...",
  cached_notice: "首次加载约30-90秒，后续加载即时显示（已缓存）",
  agents_thinking: "智能体正在思考...",
  ask_investing: "任何投资问题尽管问",
  type_message: "询问股票、投资或金融概念...",
  price_chart: "价格走势图",
  chart_legend: "K线图 + SMA 20 (橙色) + SMA 50 (紫色)",
  chart_tip: "📖 如何看K线：绿色蜡烛=价格上涨，红色=下跌。细线（影线）显示当日最高和最低价。SMA均线显示一段时间的平均价格——短期均线上穿长期均线可能预示上涨趋势（\"金叉\"）。",
  disclaimer: "⚠️ 本分析仅供教育参考，不构成任何投资建议。投资有风险，过往业绩不代表未来表现。",
  dashboard: "仪表盘",
  chat: "对话",
  learn: "学习",
  overview: "概览",
};

function getTranslations(market: MarketCode): Translations {
  return market === "cn" ? CN_TRANSLATIONS : US_TRANSLATIONS;
}

// ── Context ─────────────────────────────────────────────────────────

interface MarketContextType {
  market: MarketCode;
  setMarket: (m: MarketCode) => void;
  t: Translations;
  marketData: MarketData | null;
  currencySymbol: string;
  locale: string;
}

const MarketContext = createContext<MarketContextType>({
  market: "us",
  setMarket: () => {},
  t: US_TRANSLATIONS,
  marketData: null,
  currencySymbol: "$",
  locale: "en-US",
});

const MARKET_STORAGE_KEY = "stockwise_market";

export function MarketProvider({ children }: { children: ReactNode }) {
  // Always start with "us" for SSR — load saved preference in useEffect
  const [market, setMarketState] = useState<MarketCode>("us");
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Load saved market from localStorage after hydration (avoids SSR mismatch)
  useEffect(() => {
    const saved = localStorage.getItem(MARKET_STORAGE_KEY) as MarketCode;
    if (saved && (saved === "us" || saved === "cn")) {
      setMarketState(saved);
    }
    setHydrated(true);
  }, []);

  // Persist + set market
  const setMarket = (m: MarketCode) => {
    localStorage.setItem(MARKET_STORAGE_KEY, m);
    setMarketState(m);
  };

  // Fetch market config from backend
  useEffect(() => {
    if (!hydrated) return;
    fetch(`/api/v1/market?market=${market}`)
      .then((r) => r.json())
      .then(setMarketData)
      .catch(() => {});
  }, [hydrated, market]);

  const value: MarketContextType = {
    market,
    setMarket,
    t: getTranslations(market),
    marketData,
    currencySymbol: market === "cn" ? "¥" : "$",
    locale: market === "cn" ? "zh-CN" : "en-US",
  };

  return (
    <MarketContext.Provider value={value}>{children}</MarketContext.Provider>
  );
}

export function useMarket() {
  return useContext(MarketContext);
}

// ── User API key (per-user, stored locally, never sent to our server) ──

const API_KEY_STORAGE = "stockwise_user_api_key";

export function getUserApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(API_KEY_STORAGE);
}

export function setUserApiKey(key: string) {
  localStorage.setItem(API_KEY_STORAGE, key);
}

export function clearUserApiKey() {
  localStorage.removeItem(API_KEY_STORAGE);
}

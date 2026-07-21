"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { TrendingUp, ChevronRight, Key, Eye, EyeOff } from "lucide-react";
import { useMarket, type MarketCode, getUserApiKey, setUserApiKey } from "@/lib/market-context";

export default function LandingPage() {
  const router = useRouter();
  const { market, setMarket, t } = useMarket();
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [keySaved, setKeySaved] = useState(false);

  useEffect(() => {
    const saved = getUserApiKey();
    if (saved) { setApiKey(saved); setKeySaved(true); }
  }, []);

  const saveKey = () => {
    if (apiKey.trim()) { setUserApiKey(apiKey.trim()); setKeySaved(true); }
  };

  const clearKey = () => {
    setApiKey(""); setKeySaved(false);
    // Clear from storage
    if (typeof window !== "undefined") localStorage.removeItem("stockwise_user_api_key");
  };

  const handleEnter = () => {
    router.push("/dashboard");
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-950 px-6">
      {/* Logo */}
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600">
          <TrendingUp className="h-7 w-7 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-white">StockWise</h1>
      </div>
      <p className="mb-4 text-lg text-gray-400">
        {market === "cn" ? "AI驱动的股票投资学习助手" : "AI-Powered Stock Investment Learning"}
      </p>
      <p className="mb-12 max-w-md text-center text-sm text-gray-600">
        {market === "cn"
          ? "选择市场，AI智能体帮您分析股票财务、新闻和技术指标"
          : "Select your market. AI agents analyze financials, news, and technical indicators — all in plain language."
        }
      </p>

      {/* Market selection cards */}
      <div className="mb-10 grid gap-5 sm:grid-cols-2 w-full max-w-xl">
        <MarketCard
          flag="🇺🇸"
          title="US Market"
          subtitle="美股市场"
          tickers="AAPL · GOOGL · NVDA · TSLA · MSFT"
          currency="USD · $"
          active={market === "us"}
          onClick={() => setMarket("us")}
        />
        <MarketCard
          flag="🇨🇳"
          title="中国A股"
          subtitle="China A-Share Market"
          tickers="茅台 · 比亚迪 · 宁德时代 · 五粮液"
          currency="CNY · ¥"
          active={market === "cn"}
          onClick={() => setMarket("cn")}
        />
      </div>

      {/* API Key */}
      <div className="mb-8 w-full max-w-xl rounded-xl border border-gray-700 bg-gray-900/50 p-5">
        <div className="flex items-center gap-2 mb-3">
          <Key className="h-4 w-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white">
            {market === "cn" ? "Anthropic API 密钥" : "Anthropic API Key"}
          </h3>
        </div>
        <p className="mb-3 text-xs text-gray-500">
          {market === "cn"
            ? "每个用户使用自己的API密钥——费用由各自承担，密钥仅保存在您的浏览器中。"
            : "Each user uses their own API key — you only pay for your own usage. Key is stored only in your browser."
          }
          {" "}
          <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-blue-400 underline">
            {market === "cn" ? "获取密钥" : "Get a key"}
          </a>
        </p>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type={showKey ? "text" : "password"}
              value={apiKey}
              onChange={(e) => { setApiKey(e.target.value); setKeySaved(false); }}
              placeholder="sk-ant-api03-..."
              className="w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2.5 pr-10 text-sm text-white placeholder-gray-600 focus:border-blue-500 focus:outline-none"
            />
            <button
              onClick={() => setShowKey(!showKey)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
            >
              {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {keySaved ? (
            <button
              onClick={clearKey}
              className="rounded-lg bg-red-600/20 px-4 py-2.5 text-sm font-medium text-red-400 transition hover:bg-red-600/30"
            >
              {market === "cn" ? "清除" : "Clear"}
            </button>
          ) : (
            <button
              onClick={saveKey}
              disabled={!apiKey.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-40"
            >
              {market === "cn" ? "保存" : "Save"}
            </button>
          )}
        </div>
        {keySaved && (
          <p className="mt-2 text-xs text-green-400">
            ✓ {market === "cn" ? "密钥已保存" : "API key saved"} — {market === "cn" ? "仅保存在此浏览器中" : "stored only in this browser"}
          </p>
        )}
      </div>

      {/* CTA */}
      <button
        onClick={handleEnter}
        className="group flex items-center gap-2 rounded-xl bg-blue-600 px-10 py-4 text-lg font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:bg-blue-500 hover:shadow-blue-500/30"
      >
        {market === "cn" ? "进入仪表盘" : "Enter Dashboard"}
        <ChevronRight className="h-5 w-5 transition group-hover:translate-x-0.5" />
      </button>

      <p className="mt-6 text-xs text-gray-700">
        ⚠️ {market === "cn"
          ? "仅供教育参考，不构成投资建议"
          : "For educational purposes only. Not financial advice."}
      </p>
    </div>
  );
}

function MarketCard({
  flag,
  title,
  subtitle,
  tickers,
  currency,
  active,
  onClick,
}: {
  flag: string;
  title: string;
  subtitle: string;
  tickers: string;
  currency: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-2xl border-2 p-6 text-left transition ${
        active
          ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10"
          : "border-gray-700 bg-gray-900/50 hover:border-gray-500"
      }`}
    >
      <div className="mb-3 text-4xl">{flag}</div>
      <h3 className={`mb-1 text-lg font-bold ${active ? "text-blue-400" : "text-white"}`}>
        {title}
      </h3>
      <p className="mb-3 text-xs text-gray-500">{subtitle}</p>
      <p className="mb-2 text-xs text-gray-400">{tickers}</p>
      <p className="text-xs text-gray-600">{currency}</p>
      {active && (
        <div className="mt-3 inline-flex items-center gap-1 rounded-full bg-blue-600/20 px-3 py-1 text-xs font-medium text-blue-400">
          ✓ {title === "US Market" ? "Selected" : "已选择"}
        </div>
      )}
    </button>
  );
}

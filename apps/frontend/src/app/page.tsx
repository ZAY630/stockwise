"use client";

import { useRouter } from "next/navigation";
import { TrendingUp, ChevronRight } from "lucide-react";
import { useMarket, type MarketCode } from "@/lib/market-context";

export default function LandingPage() {
  const router = useRouter();
  const { market, setMarket, t } = useMarket();

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

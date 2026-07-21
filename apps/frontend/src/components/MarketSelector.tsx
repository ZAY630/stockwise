"use client";

import { useMarket, type MarketCode } from "@/lib/market-context";

export default function MarketSelector() {
  const { market, setMarket } = useMarket();

  const options: { code: MarketCode; flag: string; label: string }[] = [
    { code: "us", flag: "🇺🇸", label: "US" },
    { code: "cn", flag: "🇨🇳", label: "中国" },
  ];

  return (
    <div className="flex items-center rounded-lg bg-gray-800/70 p-0.5">
      {options.map((opt) => (
        <button
          key={opt.code}
          onClick={() => setMarket(opt.code)}
          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition ${
            market === opt.code
              ? "bg-blue-600 text-white shadow-sm"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <span className="text-sm">{opt.flag}</span>
          {opt.label}
        </button>
      ))}
    </div>
  );
}

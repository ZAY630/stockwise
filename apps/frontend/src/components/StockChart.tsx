"use client";

import { useEffect, useRef, useState } from "react";
import type { IChartApi, ISeriesApi, CandlestickData, HistogramData, LineData } from "lightweight-charts";
import { apiGet } from "@/lib/api-client";
import { useMarket } from "@/lib/market-context";
import type { OHLCVPoint } from "@/types/common";

// Lazy-load the chart library (browser-only, uses Canvas)
let createChart: any = null;
let ColorType: any = null;

async function loadChartLib() {
  if (!createChart) {
    const mod = await import("lightweight-charts");
    createChart = mod.createChart;
    ColorType = mod.ColorType;
  }
  return { createChart, ColorType };
}

interface StockChartProps { symbol: string; }

type Period = "1mo" | "3mo" | "6mo" | "1y" | "2y" | "5y";

const PERIODS: { key: Period; label: string }[] = [
  { key: "1mo", label: "1M" }, { key: "3mo", label: "3M" },
  { key: "6mo", label: "6M" }, { key: "1y", label: "1Y" },
  { key: "2y", label: "2Y" }, { key: "5y", label: "5Y" },
];

// SMA configuration per market — matching real trading platforms
interface SmaConfig { period: number; color: string; label: string; lineStyle?: number; }

const SMA_CONFIGS: Record<string, SmaConfig[]> = {
  // China: 同花顺/东方财富 standard — 5日(白), 20日(黄), 60日(紫)
  cn: [
    { period: 5, color: "#FFFFFF", label: "MA5" },
    { period: 20, color: "#F59E0B", label: "MA20" },
    { period: 60, color: "#8B5CF6", label: "MA60" },
  ],
  // US: TradingView standard — 20(黄), 50(紫), 200(蓝虚线)
  us: [
    { period: 20, color: "#F59E0B", label: "SMA20" },
    { period: 50, color: "#8B5CF6", label: "SMA50" },
    { period: 200, color: "#3B82F6", label: "SMA200", lineStyle: 2 },
  ],
};

// Helper: compute SMA for a given period
function computeSMA(closes: number[], period: number, times: any[]): LineData[] {
  if (closes.length < period) return [];
  const data: LineData[] = [];
  for (let i = period - 1; i < closes.length; i++) {
    const sum = closes.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
    data.push({ time: times[i], value: sum / period });
  }
  return data;
}

export default function StockChart({ symbol }: StockChartProps) {
  const { market } = useMarket();
  const smaConfigs = SMA_CONFIGS[market] || SMA_CONFIGS["us"];
  const displaySymbol = (s: string) => s.replace(/\.(SS|SZ)$/, "");

  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const smaSeriesRefs = useRef<ISeriesApi<"Line">[]>([]);

  const [chartReady, setChartReady] = useState(false);
  const [period, setPeriod] = useState<Period>("1y");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;
    let cancelled = false;

    loadChartLib().then(({ createChart, ColorType }) => {
      if (cancelled || !chartContainerRef.current) return;

      const chart = createChart(chartContainerRef.current, {
        layout: { background: { type: ColorType.Solid, color: "transparent" }, textColor: "#94A3B8" },
        grid: { vertLines: { color: "rgba(51, 65, 85, 0.4)" }, horzLines: { color: "rgba(51, 65, 85, 0.4)" } },
        crosshair: { mode: 0 },
        rightPriceScale: { borderColor: "rgba(51, 65, 85, 0.6)", scaleMargins: { top: 0.05, bottom: 0.25 } },
        timeScale: { borderColor: "rgba(51, 65, 85, 0.6)", timeVisible: true },
        width: chartContainerRef.current.clientWidth,
        height: 420,
      });
      chartRef.current = chart;

      // Candlestick
      candlestickSeriesRef.current = chart.addCandlestickSeries({
        upColor: "#22C55E", downColor: "#EF4444",
        borderUpColor: "#22C55E", borderDownColor: "#EF4444",
        wickUpColor: "#22C55E", wickDownColor: "#EF4444",
      });

      // Volume
      const vSeries = chart.addHistogramSeries({
        color: "rgba(59, 130, 246, 0.4)", priceFormat: { type: "volume" }, priceScaleId: "",
      });
      volumeSeriesRef.current = vSeries;
      vSeries.priceScale().applyOptions({ scaleMargins: { top: 0.78, bottom: 0 } });

      // SMA lines (dynamic per market)
      smaSeriesRefs.current = smaConfigs.map((cfg) =>
        chart.addLineSeries({
          color: cfg.color,
          lineWidth: cfg.period === 200 ? 1 : 1.5,
          lineStyle: cfg.lineStyle || 0,
          priceLineVisible: false,
          lastValueVisible: false,
        })
      );

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
        }
      };
      window.addEventListener("resize", handleResize);
      (chart as any)._resizeHandler = handleResize;
      setChartReady(true);
    });

    return () => {
      cancelled = true;
      if (chartRef.current) {
        const h = (chartRef.current as any)._resizeHandler;
        if (h) window.removeEventListener("resize", h);
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  // Fetch and update chart data
  useEffect(() => {
    if (!chartReady || !candlestickSeriesRef.current || !volumeSeriesRef.current) return;

    setLoading(true);
    setError(null);

    // Clear all series
    candlestickSeriesRef.current.setData([]);
    volumeSeriesRef.current.setData([]);
    smaSeriesRefs.current.forEach((s) => s.setData([]));

    apiGet<{ symbol: string; period: string; interval: string; data: OHLCVPoint[] }>(
      `/stocks/${symbol}/history?period=${period}&interval=1d`
    )
      .then((res) => {
        const rawData = res.data || [];
        if (rawData.length === 0) { setError("No chart data available yet."); setLoading(false); return; }

        const candleData: CandlestickData[] = [];
        const volumeData: HistogramData[] = [];
        const closes: number[] = [];
        const times: any[] = [];

        for (const point of rawData) {
          const time = (new Date(point.date).getTime() / 1000) as any;
          if (isNaN(time as any)) continue;
          times.push(time);
          candleData.push({ time, open: point.open, high: point.high, low: point.low, close: point.close });
          volumeData.push({
            time, value: point.volume,
            color: point.close >= point.open ? "rgba(34, 197, 94, 0.35)" : "rgba(239, 68, 68, 0.35)",
          });
          closes.push(point.close);
        }

        candlestickSeriesRef.current!.setData(candleData);
        volumeSeriesRef.current!.setData(volumeData);

        // Compute each SMA
        smaSeriesRefs.current.forEach((series, idx) => {
          const cfg = smaConfigs[idx];
          series.setData(computeSMA(closes, cfg.period, times));
        });

        setLoading(false);
      })
      .catch(() => { setError("Could not load chart data. Try again later."); setLoading(false); });
  }, [chartReady, symbol, period]);

  const isCN = market === "cn";
  const tipText = isCN
    ? "📖 如何看K线：绿色=上涨，红色=下跌。影线=当日最高/最低价。MA5=5日均线（白色），MA20=20日均线（黄色），MA60=60日均线（紫色）。短期均线上穿长期均线可能预示上涨趋势（\"金叉\"）。"
    : "📖 How to read: Green=up, red=down. Wicks=day high/low. SMA20=yellow, SMA50=purple, SMA200=blue (dashed). Golden Cross = short SMA crosses above long SMA → uptrend signal.";

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-200">{displaySymbol(symbol)} — {isCN ? "K线图" : "Price Chart"}</h3>
          <p className="text-xs text-gray-500">
            {smaConfigs.map((c) => c.label).join(" + ")} + Volume
          </p>
        </div>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button key={p.key} onClick={() => setPeriod(p.key)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                period === p.key ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200"
              }`}>{p.label}</button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mb-3 flex gap-5 text-xs text-gray-500">
        {smaConfigs.map((cfg, i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: cfg.color }} />
            {cfg.label}
          </span>
        ))}
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-blue-500/40" />Vol
        </span>
      </div>

      {/* Chart */}
      <div className="relative min-h-[420px]">
        {loading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-gray-950/60">
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
              {isCN ? "加载中..." : "Loading chart..."}
            </div>
          </div>
        )}
        {error && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-gray-950/60">
            <p className="text-sm text-gray-500">{error}</p>
          </div>
        )}
        <div ref={chartContainerRef} className="w-full" />
      </div>

      <div className="mt-3 rounded-lg bg-blue-500/5 border border-blue-500/20 px-4 py-2.5">
        <p className="text-xs text-blue-300">{tipText}</p>
      </div>
    </div>
  );
}

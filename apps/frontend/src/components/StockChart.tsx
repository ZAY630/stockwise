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

interface StockChartProps {
  symbol: string;
}

type Period = "1mo" | "3mo" | "6mo" | "1y" | "2y" | "5y";

const PERIODS: { key: Period; label: string }[] = [
  { key: "1mo", label: "1M" },
  { key: "3mo", label: "3M" },
  { key: "6mo", label: "6M" },
  { key: "1y", label: "1Y" },
  { key: "2y", label: "2Y" },
  { key: "5y", label: "5Y" },
];

export default function StockChart({ symbol }: StockChartProps) {
  const { t, locale } = useMarket();
  const displaySymbol = (s: string) => s.replace(/\.(SS|SZ)$/, "");
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const sma20SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const sma50SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);

  const [chartReady, setChartReady] = useState(false);
  const [period, setPeriod] = useState<Period>("1y");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize chart (lazy-loads lightweight-charts which uses Canvas)
  useEffect(() => {
    if (!chartContainerRef.current) return;
    let cancelled = false;

    loadChartLib().then(({ createChart, ColorType }) => {
      if (cancelled || !chartContainerRef.current) return;

      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: "transparent" },
          textColor: "#94A3B8",
        },
        grid: {
          vertLines: { color: "rgba(51, 65, 85, 0.4)" },
          horzLines: { color: "rgba(51, 65, 85, 0.4)" },
        },
        crosshair: { mode: 0 },
        rightPriceScale: {
          borderColor: "rgba(51, 65, 85, 0.6)",
          scaleMargins: { top: 0.05, bottom: 0.25 },
        },
        timeScale: {
          borderColor: "rgba(51, 65, 85, 0.6)",
          timeVisible: true,
        },
        width: chartContainerRef.current.clientWidth,
        height: 420,
      });
      chartRef.current = chart;

      // Candlestick series
      const cSeries = chart.addCandlestickSeries({
        upColor: "#22C55E", downColor: "#EF4444",
        borderUpColor: "#22C55E", borderDownColor: "#EF4444",
        wickUpColor: "#22C55E", wickDownColor: "#EF4444",
      });
      candlestickSeriesRef.current = cSeries;

      // Volume series
      const vSeries = chart.addHistogramSeries({
        color: "rgba(59, 130, 246, 0.4)",
        priceFormat: { type: "volume" },
        priceScaleId: "",
      });
      volumeSeriesRef.current = vSeries;
      vSeries.priceScale().applyOptions({ scaleMargins: { top: 0.78, bottom: 0 } });

      // SMA 20 line
      sma20SeriesRef.current = chart.addLineSeries({
        color: "#F59E0B", lineWidth: 1.5,
        priceLineVisible: false, lastValueVisible: false,
      });

      // SMA 50 line
      sma50SeriesRef.current = chart.addLineSeries({
        color: "#8B5CF6", lineWidth: 1.5,
        priceLineVisible: false, lastValueVisible: false,
      });

      // Resize handler
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
        }
      };
      window.addEventListener("resize", handleResize);
      // Store for cleanup
      (chart as any)._resizeHandler = handleResize;
      // Signal that chart is ready for data
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

  // Fetch and update data when chart is ready or period changes
  useEffect(() => {
    if (!chartReady) return;
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || !sma20SeriesRef.current || !sma50SeriesRef.current) return;

    setLoading(true);
    setError(null);

    apiGet<{ symbol: string; period: string; interval: string; data: OHLCVPoint[] }>(
      `/stocks/${symbol}/history?period=${period}&interval=1d`
    )
      .then((res) => {
        const rawData = res.data || [];
        if (rawData.length === 0) {
          setError("No chart data available yet.");
          setLoading(false);
          return;
        }

        // Build candlestick data
        const candleData: CandlestickData[] = [];
        const volumeData: HistogramData[] = [];
        const closes: number[] = [];

        for (const point of rawData) {
          const time = (new Date(point.date).getTime() / 1000) as any;
          // Skip invalid dates
          if (isNaN(time as any)) continue;

          candleData.push({
            time,
            open: point.open,
            high: point.high,
            low: point.low,
            close: point.close,
          });
          volumeData.push({
            time,
            value: point.volume,
            color: point.close >= point.open
              ? "rgba(34, 197, 94, 0.35)"
              : "rgba(239, 68, 68, 0.35)",
          });
          closes.push(point.close);
        }

        candlestickSeriesRef.current!.setData(candleData);
        volumeSeriesRef.current!.setData(volumeData);

        // Compute SMA 20 overlay
        if (closes.length >= 20) {
          const sma20Data: LineData[] = [];
          for (let i = 19; i < closes.length; i++) {
            const sum = closes.slice(i - 19, i + 1).reduce((a, b) => a + b, 0);
            sma20Data.push({ time: candleData[i].time, value: sum / 20 });
          }
          sma20SeriesRef.current!.setData(sma20Data);
        }

        // Compute SMA 50 overlay
        if (closes.length >= 50) {
          const sma50Data: LineData[] = [];
          for (let i = 49; i < closes.length; i++) {
            const sum = closes.slice(i - 49, i + 1).reduce((a, b) => a + b, 0);
            sma50Data.push({ time: candleData[i].time, value: sum / 50 });
          }
          sma50SeriesRef.current!.setData(sma50Data);
        }

        setLoading(false);
      })
      .catch(() => {
        setError("Could not load chart data. Try again later.");
        setLoading(false);
      });
  }, [chartReady, symbol, period]);

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
      {/* Header with period selector */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-200">
            {displaySymbol(symbol)} — {t.price_chart}
          </h3>
          <p className="text-xs text-gray-500">{t.chart_legend}</p>
        </div>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                period === p.key
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mb-3 flex gap-6 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-amber-500" />
          SMA 20
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-purple-500" />
          SMA 50
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-blue-500/40" />
          Volume
        </span>
      </div>

      {/* Chart area */}
      <div className="relative min-h-[420px]">
        {loading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-lg bg-gray-950/60">
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
              Loading chart...
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

      {/* Beginner-friendly tip */}
      <div className="mt-3 rounded-lg bg-blue-500/5 border border-blue-500/20 px-4 py-2.5">
        <p className="text-xs text-blue-300">{t.chart_tip}</p>
      </div>
    </div>
  );
}

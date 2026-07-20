"""Technical analysis service using the ta library.

Computes common technical indicators from OHLCV price data.
All computation is local (no API calls needed).
"""

from typing import Any

import pandas as pd
import ta


class TechnicalService:
    """Computes technical indicators from OHLCV data."""

    @staticmethod
    def compute_indicators(ohlcv_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Compute a full suite of technical indicators from price history.

        Args:
            ohlcv_data: List of dicts with keys: date, open, high, low, close, volume

        Returns:
            Dict with indicator arrays and latest-value interpretations.
        """
        if not ohlcv_data:
            return {"error": "No data provided"}

        df = pd.DataFrame(ohlcv_data)
        required_cols = {"close", "high", "low", "volume"}
        available = required_cols & set(c.lower() for c in df.columns)

        if len(available) < 3:
            return {"error": f"Insufficient data columns. Need close/high/low/volume, got: {available}"}

        # Normalize column names to lowercase
        col_map = {}
        for c in df.columns:
            if c.lower() == "close":
                col_map[c] = "close"
            elif c.lower() == "high":
                col_map[c] = "high"
            elif c.lower() == "low":
                col_map[c] = "low"
            elif c.lower() == "volume":
                col_map[c] = "volume"
            elif c.lower() == "open":
                col_map[c] = "open"
        df = df.rename(columns=col_map)

        close = df["close"].astype(float)
        high = df["high"].astype(float) if "high" in df else close
        low = df["low"].astype(float) if "low" in df else close
        volume = df["volume"].astype(float) if "volume" in df else pd.Series([0] * len(close))

        indicators: dict[str, Any] = {}

        # RSI (Relative Strength Index)
        try:
            rsi_series = ta.momentum.RSIIndicator(close, window=14).rsi()
            latest_rsi = float(rsi_series.dropna().iloc[-1]) if not rsi_series.dropna().empty else None
            indicators["rsi"] = {
                "latest": round(latest_rsi, 2) if latest_rsi else None,
                "interpretation": TechnicalService._interpret_rsi(latest_rsi),
            }
        except Exception:
            indicators["rsi"] = {"latest": None, "interpretation": "unavailable"}

        # MACD
        try:
            macd = ta.trend.MACD(close)
            macd_vals = macd.macd()
            signal_vals = macd.macd_signal()
            latest_macd = float(macd_vals.dropna().iloc[-1]) if not macd_vals.dropna().empty else None
            latest_signal = float(signal_vals.dropna().iloc[-1]) if not signal_vals.dropna().empty else None
            indicators["macd"] = {
                "latest": round(latest_macd, 4) if latest_macd else None,
                "signal": round(latest_signal, 4) if latest_signal else None,
                "interpretation": TechnicalService._interpret_macd(latest_macd, latest_signal),
            }
        except Exception:
            indicators["macd"] = {"latest": None, "signal": None, "interpretation": "unavailable"}

        # Simple Moving Averages
        for window in [20, 50, 200]:
            try:
                if len(close) >= window:
                    sma = ta.trend.SMAIndicator(close, window=window).sma_indicator()
                    latest = float(sma.dropna().iloc[-1]) if not sma.dropna().empty else None
                    indicators[f"sma_{window}"] = {
                        "latest": round(latest, 2) if latest else None,
                    }
                else:
                    indicators[f"sma_{window}"] = {"latest": None}
            except Exception:
                indicators[f"sma_{window}"] = {"latest": None}

        # Trend interpretation (close vs SMAs)
        latest_close = float(close.iloc[-1])
        sma_20 = indicators.get("sma_20", {}).get("latest")
        sma_50 = indicators.get("sma_50", {}).get("latest")
        indicators["trend"] = TechnicalService._interpret_trend(latest_close, sma_20, sma_50)

        # Bollinger Bands
        try:
            bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
            indicators["bollinger"] = {
                "upper": round(float(bb.bollinger_hband().dropna().iloc[-1]), 2) if not bb.bollinger_hband().dropna().empty else None,
                "middle": round(float(bb.bollinger_mavg().dropna().iloc[-1]), 2) if not bb.bollinger_mavg().dropna().empty else None,
                "lower": round(float(bb.bollinger_lband().dropna().iloc[-1]), 2) if not bb.bollinger_lband().dropna().empty else None,
            }
        except Exception:
            indicators["bollinger"] = {"upper": None, "middle": None, "lower": None}

        # ATR (Average True Range) - volatility
        try:
            atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
            latest_atr = float(atr.dropna().iloc[-1]) if not atr.dropna().empty else None
            indicators["atr"] = {
                "latest": round(latest_atr, 2) if latest_atr else None,
            }
        except Exception:
            indicators["atr"] = {"latest": None}

        # OBV (On-Balance Volume)
        try:
            obv = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
            latest_obv = float(obv.dropna().iloc[-1]) if not obv.dropna().empty else None
            indicators["obv"] = {"latest": int(latest_obv) if latest_obv else None}
        except Exception:
            indicators["obv"] = {"latest": None}

        # Current price
        indicators["current_price"] = round(latest_close, 2)

        return indicators

    @staticmethod
    def _interpret_rsi(rsi: float | None) -> str:
        """Interpret RSI value."""
        if rsi is None:
            return "No RSI data available"
        if rsi > 70:
            return f"Overbought ({rsi:.1f}) — stock may be overvalued short-term, potential pullback"
        if rsi < 30:
            return f"Oversold ({rsi:.1f}) — stock may be undervalued short-term, potential bounce"
        if rsi > 60:
            return f"Bullish momentum ({rsi:.1f}) — upward pressure but not extreme"
        if rsi < 40:
            return f"Bearish momentum ({rsi:.1f}) — downward pressure but not extreme"
        return f"Neutral ({rsi:.1f}) — no strong momentum either way"

    @staticmethod
    def _interpret_macd(macd: float | None, signal: float | None) -> str:
        """Interpret MACD relative to signal line."""
        if macd is None or signal is None:
            return "No MACD data available"
        if macd > signal:
            if macd > 0:
                return f"Bullish (MACD {macd:.4f} > Signal {signal:.4f}) — upward momentum, above zero line"
            return f"Recovering (MACD {macd:.4f} > Signal {signal:.4f}) — momentum improving but still below zero"
        else:
            if macd < 0:
                return f"Bearish (MACD {macd:.4f} < Signal {signal:.4f}) — downward momentum, below zero line"
            return f"Weakening (MACD {macd:.4f} < Signal {signal:.4f}) — momentum fading but still above zero"

    @staticmethod
    def _interpret_trend(price: float, sma_20: float | None, sma_50: float | None) -> str:
        """Interpret price relative to moving averages."""
        if sma_20 is None and sma_50 is None:
            return "Insufficient data for trend analysis"

        parts = []
        if sma_20:
            if price > sma_20:
                parts.append(f"Above 20-day SMA (${sma_20:.2f}) — short-term bullish")
            else:
                parts.append(f"Below 20-day SMA (${sma_20:.2f}) — short-term bearish")

        if sma_50:
            if price > sma_50:
                parts.append(f"Above 50-day SMA (${sma_50:.2f}) — medium-term bullish")
            else:
                parts.append(f"Below 50-day SMA (${sma_50:.2f}) — medium-term bearish")

        # Golden cross / death cross
        if sma_20 and sma_50:
            if sma_20 > sma_50:
                parts.append("Golden Cross (20-day above 50-day) — bullish signal")
            else:
                parts.append("Death Cross (20-day below 50-day) — bearish signal")

        return " | ".join(parts)

import numpy as np
import pandas as pd


class TradingEngine:

    def __init__(
        self,
        risk_per_trade_pct: float = 0.01,
        min_confluence_pct: float = 70.0,
    ):
        """Engine parameters for risk management and trade execution validation."""
        self.risk_per_trade_pct = risk_per_trade_pct
        self.min_confluence_pct = min_confluence_pct

    # ==========================================
    # 1. INDICATOR CALCULATIONS & DATA CLEANING
    # ==========================================
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates RSI, ATR, and ADX cleanly without leaving NaN values."""
        df = df.copy()

        # Clean raw OHLC data inputs
        df[["open", "high", "low", "close"]] = df[
            ["open", "high", "low", "close"]
        ].apply(pd.to_numeric, errors="coerce")
        df = df.ffill().bfill()

        # 1. Relative Strength Index (RSI - 14)
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        rs = avg_gain / (avg_loss.replace(0, np.nan))
        df["rsi"] = 100 - (100 / (1 + rs))

        # 2. Average True Range (ATR - 14)
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - df["close"].shift(1)).abs()
        tr3 = (df["low"] - df["close"].shift(1)).abs()
        df["tr"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["atr"] = df["tr"].rolling(window=14, min_periods=1).mean()

        # 3. Average Directional Index (ADX - 14)
        up_move = df["high"] - df["high"].shift(1)
        down_move = df["low"].shift(1) - df["low"]

        df["plus_dm"] = np.where(
            (up_move > down_move) & (up_move > 0), up_move, 0.0
        )
        df["minus_dm"] = np.where(
            (down_move > up_move) & (down_move > 0), down_move, 0.0
        )

        smooth_plus = df["plus_dm"].rolling(window=14, min_periods=1).mean()
        smooth_minus = df["minus_dm"].rolling(window=14, min_periods=1).mean()

        plus_di = 100 * (smooth_plus / df["atr"].replace(0, np.nan))
        minus_di = 100 * (smooth_minus / df["atr"].replace(0, np.nan))

        di_diff = (plus_di - minus_di).abs()
        di_sum = plus_di + minus_di
        dx = 100 * (di_diff / di_sum.replace(0, np.nan))
        df["adx"] = dx.rolling(window=14, min_periods=1).mean()

        # Backfill/Forwardfill remaining indicator setup gaps to prevent NaN
        df = df.ffill().bfill()
        return df

    # ==========================================
    # 2. SIGNAL GENERATION & CONFLUENCE EVAL
    # ==========================================
    def evaluate_market(
        self, df: pd.DataFrame, htf_bias: str, account_balance: float
    ) -> dict:
        """Evaluates confluence metrics, risk controls, and output parameters."""
        df = self.calculate_indicators(df)
        latest = df.iloc[-1]

        price = float(latest["close"])
        rsi = float(latest["rsi"])
        adx = float(latest["adx"])
        atr = float(latest["atr"])

        # DATA GUARD: If any vital reading is NaN, block execution immediately
        if np.isnan([price, rsi, adx, atr]).any():
            return {
                "signal": "NEUTRAL",
                "reason": "DATA_ERROR: Invalid or NaN indicators",
                "confluence": 0.0,
                "stability": "STABILITY LOW (0%): DATA CORRUPTED",
            }

        # Confluence Weight Scoring System
        confluence_score = 0.0

        # HTF Trend Alignment (40%)
        if htf_bias.upper() in ["BULLISH", "BEARISH"]:
            confluence_score += 40.0

        # ADX Trend Strength Guard (30%)
        if adx >= 20.0:
            confluence_score += 30.0

        # RSI Momentum Boundaries (30%)
        rsi_bullish = 45.0 <= rsi <= 68.0
        rsi_bearish = 32.0 <= rsi <= 55.0

        if htf_bias.upper() == "BULLISH" and rsi_bullish:
            confluence_score += 30.0
        elif htf_bias.upper() == "BEARISH" and rsi_bearish:
            confluence_score += 30.0

        # ==========================================
        # 3. DIRECTION & DYNAMIC RISK CONTROL
        # ==========================================
        signal = "NEUTRAL"
        stop_loss = 0.0
        take_profit = 0.0
        position_size = 0.0

        # Ensure trade only triggers if confluence threshold is satisfied
        if confluence_score >= self.min_confluence_pct:
            if htf_bias.upper() == "BEARISH" and rsi_bearish:
                signal = "SELL"
                stop_loss = round(price + (1.5 * atr), 2)
                take_profit = round(price - (3.0 * atr), 2)
            elif htf_bias.upper() == "BULLISH" and rsi_bullish:
                signal = "BUY"
                stop_loss = round(price - (1.5 * atr), 2)
                take_profit = round(price + (3.0 * atr), 2)

        # Dynamic Lot Sizing based on Account Risk (1% Risk Rule)
        if signal != "NEUTRAL":
            risk_amount = account_balance * self.risk_per_trade_pct
            sl_distance = abs(price - stop_loss)
            if sl_distance > 0:
                position_size = round(risk_amount / sl_distance, 2)

        stability_status = (
            f"STABILITY HIGH ({int(confluence_score)}%): ENTER {signal}"
            if signal != "NEUTRAL"
            else f"STABILITY LOW ({int(confluence_score)}%): NO TRADE / WAIT"
        )

        return {
            "symbol": "GOLD (XAU/USD)",
            "price": round(price, 2),
            "signal": signal,
            "confluence": round(confluence_score, 1),
            "technical_indicators": {
                "rsi": round(rsi, 1),
                "adx": round(adx, 1),
                "atr": round(atr, 2),
                "htf_bias": htf_bias.upper(),
            },
            "risk_management": {
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "position_size": position_size,
                "risk_amount_usd": account_balance * self.risk_per_trade_pct,
            },
            "strategy_guidance": stability_status,
        }


# ==========================================
# EXAMPLE RUN & DRIVER CODE
# ==========================================
if __name__ == "__main__":
    # Generate dummy market candles for demonstration
    data = {
        "open": [4410.0, 4412.5, 4408.0, 4405.0, 4402.0, 4400.0, 4398.0] * 3,
        "high": [4415.0, 4414.0, 4410.0, 4407.0, 4405.0, 4403.0, 4401.0] * 3,
        "low": [4405.0, 4407.0, 4401.0, 4399.0, 4395.0, 4392.0, 4390.0] * 3,
        "close": [4412.0, 4408.0, 4404.0, 4401.0, 4396.0, 4394.0, 4391.0] * 3,
    }
    df_market = pd.DataFrame(data)

    bot = TradingEngine(risk_per_trade_pct=0.01, min_confluence_pct=70.0)
    output = bot.evaluate_market(
        df=df_market, htf_bias="BEARISH", account_balance=200.00
    )

    import json

    print(json.dumps(output, indent=4))

import yfinance as yf
import pandas as pd
import numpy as np

class TradeGuideEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def fetch_data(self, interval="1d"):
        try:
            stock = yf.Ticker(self.ticker)
            # Fetch more data (up to 1 year) to find better Swing Highs/Lows
            period = "1y" if interval == "1d" else "1mo" 
            self.data = stock.history(period=period, interval=interval)
            
            if self.data.empty: return False
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def calculate_smart_money(self, df):
        """
        Detects Order Blocks (OB) and Fair Value Gaps (FVG).
        """
        df['OB'] = None  # Order Block (Bullish/Bearish)
        df['FVG'] = None # Fair Value Gap (Bullish/Bearish)
        
        # --- 1. FAIR VALUE GAPS (FVG) ---
        # A 3-candle pattern where the 1st and 3rd candles don't overlap, leaving a gap.
        # Bullish FVG: Low of candle[i] > High of candle[i-2]
        # Bearish FVG: High of candle[i] < Low of candle[i-2]
        for i in range(2, len(df)):
            # Bullish FVG
            if df['Low'].iloc[i] > df['High'].iloc[i-2]:
                gap_size = df['Low'].iloc[i] - df['High'].iloc[i-2]
                if gap_size > (df['Close'].iloc[i] * 0.001): # Filter tiny gaps
                    df.at[df.index[i], 'FVG'] = 'BULLISH'
            
            # Bearish FVG
            elif df['High'].iloc[i] < df['Low'].iloc[i-2]:
                gap_size = df['Low'].iloc[i-2] - df['High'].iloc[i]
                if gap_size > (df['Close'].iloc[i] * 0.001):
                    df.at[df.index[i], 'FVG'] = 'BEARISH'

        # --- 2. ORDER BLOCKS (OB) ---
        # Simplified Institutional Logic: 
        # Bullish OB = The last bearish candle before a strong bullish move (Break of Structure).
        # Bearish OB = The last bullish candle before a strong bearish move.
        # We look for a candle that is engulfed by the next 2-3 candles.
        for i in range(2, len(df)-2):
            # Bullish OB check (Red candle followed by strong Green)
            if df['Close'].iloc[i] < df['Open'].iloc[i]: # Red Candle
                # Check if next 2 candles break above this candle's High
                if df['Close'].iloc[i+1] > df['High'].iloc[i] or df['Close'].iloc[i+2] > df['High'].iloc[i]:
                     df.at[df.index[i], 'OB'] = 'BULLISH'

            # Bearish OB check (Green candle followed by strong Red)
            elif df['Close'].iloc[i] > df['Open'].iloc[i]: # Green Candle
                # Check if next 2 candles break below this candle's Low
                if df['Close'].iloc[i+1] < df['Low'].iloc[i] or df['Close'].iloc[i+2] < df['Low'].iloc[i]:
                     df.at[df.index[i], 'OB'] = 'BEARISH'

        return df

    def calculate_fibonacci(self, df):
        """
        Finds the most recent significant Swing High and Swing Low
        to calculate Fibonacci Retracement Levels.
        """
        # Look back 50 periods to find local Max/Min
        recent_data = df.tail(50)
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        
        diff = swing_high - swing_low
        
        return {
            "0.0 (Low)": swing_low,
            "0.236": swing_low + (diff * 0.236),
            "0.382": swing_low + (diff * 0.382),
            "0.5 (Mid)": swing_low + (diff * 0.5),
            "0.618 (Golden)": swing_low + (diff * 0.618),
            "1.0 (High)": swing_high
        }

    def calculate_support_resistance(self, df, window=20):
        """
        Identifies key price levels where price touched multiple times (Fractals).
        """
        levels = []
        for i in range(window, len(df) - window):
            # Check for Fractal High (Resistance)
            if df['High'].iloc[i] == max(df['High'].iloc[i-window:i+window]):
                levels.append(df['High'].iloc[i])
            # Check for Fractal Low (Support)
            elif df['Low'].iloc[i] == min(df['Low'].iloc[i-window:i+window]):
                levels.append(df['Low'].iloc[i])
        
        # Filter levels that are too close to each other
        clean_levels = []
        if levels:
            levels = sorted(levels)
            clean_levels.append(levels[0])
            for lvl in levels:
                if lvl > clean_levels[-1] * 1.01: # 1% difference required
                    clean_levels.append(lvl)
                    
        return clean_levels[-3:] # Return only top 3 most relevant levels

    def generate_signal(self, style='candle'):
        if self.data is None or self.data.empty: return None

        df = self.data.copy()
        
        # 1. Run Standard Indicators
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. Run Advanced Price Action
        df = self.calculate_smart_money(df)
        fib_levels = self.calculate_fibonacci(df)
        sr_levels = self.calculate_support_resistance(df)

        # 3. Generate Signal Score
        latest = df.iloc[-1]
        score = 0
        reasons = []

        # Standard Logic
        if latest['EMA_9'] > latest['EMA_21']:
            score += 1
            reasons.append("Bullish Trend")
        elif latest['EMA_9'] < latest['EMA_21']:
            score -= 1
            reasons.append("Bearish Trend")

        if latest['RSI'] < 30:
            score += 2
            reasons.append("RSI Oversold")
        elif latest['RSI'] > 70:
            score -= 2
            reasons.append("RSI Overbought")

        # --- NEW: SMC LOGIC ---
        # Check if we are near a Golden Ratio level
        current_price = latest['Close']
        if abs(current_price - fib_levels["0.618 (Golden)"]) < (current_price * 0.005):
            score += 1
            reasons.append("At Golden Pocket (0.618)")

        # Check for recent Order Block
        recent_obs = df.tail(5) # Look at last 5 candles
        if 'BULLISH' in recent_obs['OB'].values:
            score += 1
            reasons.append("Bullish Order Block Detected")
        elif 'BEARISH' in recent_obs['OB'].values:
            score -= 1
            reasons.append("Bearish Order Block Detected")

        # Verdict
        if score >= 2: signal = "STRONG BUY"
        elif score == 1: signal = "BUY"
        elif score == -1: signal = "SELL"
        elif score <= -2: signal = "STRONG SELL"
        else: signal = "NEUTRAL"

        sig_color = "#00e676" if "BUY" in signal else "#ff5252" if "SELL" in signal else "#ffffff"

        # Format Chart Data
        chart_data = []
        for idx, row in df.iterrows():
            ts = int(idx.timestamp() * 1000)
            chart_data.append({
                'x': ts,
                'y': [round(row['Open'], 2), round(row['High'], 2), round(row['Low'], 2), round(row['Close'], 2)]
            })

        return {
            "ticker": self.ticker,
            "current_price": round(current_price, 2),
            "signal": signal,
            "signal_color": sig_color,
            "reasons": reasons,
            "levels": {
                "entry": round(current_price, 2),
                "target": round(fib_levels["1.0 (High)"], 2), # Target is now the Swing High
                "stoploss": round(fib_levels["0.0 (Low)"], 2)  # Stop is the Swing Low
            },
            "chart_data": chart_data,
            "rsi": round(latest['RSI'], 2),
            "fib_levels": fib_levels,  # Sending these to frontend if needed
            "sr_levels": sr_levels     # Sending these to frontend if needed
        }
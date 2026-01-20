import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob  # Make sure to run: pip install textblob

class TradeGuideEngine:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None
        self.news_sentiment = 0  # Stores sentiment score (-1 to +1)

    def fetch_data(self, interval="1d"):
        try:
            # 1. Fetch Price Data
            stock = yf.Ticker(self.ticker)
            period = "1y" if interval == "1d" else "1mo"
            self.data = stock.history(period=period, interval=interval)
            
            # 2. Fetch News & Analyze Sentiment (The "High Level" Layer)
            try:
                news_list = stock.news
                sentiment_score = 0
                count = 0
                if news_list:
                    for item in news_list[:5]:  # Analyze last 5 headlines
                        blob = TextBlob(item['title'])
                        sentiment_score += blob.sentiment.polarity
                        count += 1
                    if count > 0:
                        self.news_sentiment = sentiment_score / count
            except Exception as e:
                print(f"News Error: {e}")
                self.news_sentiment = 0  # Neutral if fails
            
            if self.data.empty: return False
            return True
        except Exception as e:
            print(f"Data Fetch Error: {e}")
            return False

    # --- MARKET REGIME (ADX) ---
    def calculate_adx(self, df, period=14):
        """
        Calculates ADX to check if the market is trending or choppy.
        """
        df = df.copy()
        df['H-L'] = df['High'] - df['Low']
        df['H-C'] = abs(df['High'] - df['Close'].shift(1))
        df['L-C'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
        
        df['UpMove'] = df['High'] - df['High'].shift(1)
        df['DownMove'] = df['Low'].shift(1) - df['Low']
        
        df['+DM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0)
        df['-DM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0)
        
        # Calculate ADX
        df['+DI'] = 100 * (df['+DM'].ewm(alpha=1/period).mean() / df['TR'].ewm(alpha=1/period).mean())
        df['-DI'] = 100 * (df['-DM'].ewm(alpha=1/period).mean() / df['TR'].ewm(alpha=1/period).mean())
        df['DX'] = (abs(df['+DI'] - df['-DI']) / abs(df['+DI'] + df['-DI'])) * 100
        df['ADX'] = df['DX'].ewm(alpha=1/period).mean()
        return df

    # --- SMART MONEY CONCEPTS (SMC) ---
    def calculate_smart_money(self, df):
        df['OB'] = None
        df['FVG'] = None
        
        # 1. Fair Value Gaps
        for i in range(2, len(df)):
            if df['Low'].iloc[i] > df['High'].iloc[i-2]:
                gap = df['Low'].iloc[i] - df['High'].iloc[i-2]
                if gap > (df['Close'].iloc[i] * 0.001):
                    df.at[df.index[i], 'FVG'] = 'BULLISH'
            elif df['High'].iloc[i] < df['Low'].iloc[i-2]:
                gap = df['Low'].iloc[i-2] - df['High'].iloc[i]
                if gap > (df['Close'].iloc[i] * 0.001):
                    df.at[df.index[i], 'FVG'] = 'BEARISH'

        # 2. Order Blocks
        for i in range(2, len(df)-2):
            if df['Close'].iloc[i] < df['Open'].iloc[i]: # Red Candle
                if df['Close'].iloc[i+1] > df['High'].iloc[i]:
                     df.at[df.index[i], 'OB'] = 'BULLISH'
            elif df['Close'].iloc[i] > df['Open'].iloc[i]: # Green Candle
                if df['Close'].iloc[i+1] < df['Low'].iloc[i]:
                     df.at[df.index[i], 'OB'] = 'BEARISH'
        return df

    # --- FIBONACCI (FIXED KEYS) ---
    def calculate_fibonacci(self, df):
        recent_data = df.tail(50)
        swing_high = recent_data['High'].max()
        swing_low = recent_data['Low'].min()
        diff = swing_high - swing_low
        
        # FIXED: Using simple keys for JavaScript
        return {
            "low": swing_low,
            "mid": swing_low + (diff * 0.5),
            "golden_pocket": swing_low + (diff * 0.618),
            "high": swing_high
        }

    # --- SUPPORT & RESISTANCE ---
    def calculate_support_resistance(self, df, window=20):
        levels = []
        for i in range(window, len(df) - window):
            if df['High'].iloc[i] == max(df['High'].iloc[i-window:i+window]):
                levels.append(df['High'].iloc[i])
            elif df['Low'].iloc[i] == min(df['Low'].iloc[i-window:i+window]):
                levels.append(df['Low'].iloc[i])
        
        clean_levels = []
        if levels:
            levels = sorted(levels)
            clean_levels.append(levels[0])
            for lvl in levels:
                if lvl > clean_levels[-1] * 1.01:
                    clean_levels.append(lvl)
        return clean_levels[-3:]

    # --- GENERATE SIGNAL (FIXED RSI & JSON) ---
    def generate_signal(self, style='candle'):
        if self.data is None or self.data.empty: return None

        df = self.data.copy()
        
        # 1. Run Calculations
        df = self.calculate_adx(df)
        df = self.calculate_smart_money(df)
        
        # Standard Indicators
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / (-df['Close'].diff().where(df['Close'].diff() < 0, 0)).rolling(14).mean())))

        latest = df.iloc[-1]
        score = 0
        reasons = []

        # 2. Logic Layer (Technicals + Sentiment + SMC)
        
        # Market Regime (ADX)
        market_status = "Trending"
        if latest['ADX'] < 20:
            market_status = "Choppy (Sideways)"
            score -= 10  # Penalty for choppy market
            reasons.append("⚠️ Market is Choppy (Low ADX). Risk of fakeouts.")
        else:
            reasons.append("✅ Market is Trending (Safe).")

        # News Sentiment
        if self.news_sentiment > 0.1:
            score += 1
            reasons.append(f"📰 Positive News Sentiment ({round(self.news_sentiment, 2)})")
        elif self.news_sentiment < -0.1:
            score -= 2
            reasons.append(f"⚠️ Negative News Sentiment ({round(self.news_sentiment, 2)})")

        # Technicals
        if latest['EMA_9'] > latest['EMA_21']:
            score += 1
            reasons.append("Bullish Trend (EMA Cross)")
        
        # FIX: Handle RSI NaN
        current_rsi = latest['RSI']
        if pd.isna(current_rsi):
            current_rsi = 50.0 # Default neutral if not enough data
            
        if current_rsi < 30:
            score += 2
            reasons.append("RSI Oversold (Value Buy)")
        elif current_rsi > 70:
            score -= 2
            reasons.append("RSI Overbought (Risk)")

        # SMC
        recent_obs = df.tail(5)
        if 'BULLISH' in recent_obs['OB'].values:
            score += 1
            reasons.append("🔥 Bullish Order Block Detected")
        
        # 3. Final Signal
        if score >= 3: signal = "STRONG BUY"
        elif score >= 1: signal = "BUY"
        elif score <= -2: signal = "STRONG SELL"
        elif score <= -1: signal = "SELL"
        else: signal = "NEUTRAL / WAIT"

        # 4. Chart Data
        chart_data = []
        for idx, row in df.iterrows():
            chart_data.append({
                'x': int(idx.timestamp() * 1000),
                'y': [row['Open'], row['High'], row['Low'], row['Close']]
            })

        fib_levels = self.calculate_fibonacci(df)

        # 5. FINAL RETURN (Clean Data for Frontend)
        return {
            "ticker": self.ticker,
            "current_price": round(latest['Close'], 2),
            "signal": signal,
            "score": score,
            "adx": round(latest['ADX'], 2),
            "market_status": market_status,
            "news_sentiment": round(self.news_sentiment, 2),
            
            # --- FIXES FOR FRONTEND ---
            "rsi": round(current_rsi, 2),  # Explicitly sending RSI
            "golden_pocket": round(fib_levels["golden_pocket"], 2), # Explicitly sending GP
            
            "reasons": reasons,
            "levels": {
                "entry": round(latest['Close'], 2),
                "target": round(fib_levels["high"], 2),
                "stoploss": round(fib_levels["low"], 2)
            },
            "chart_data": chart_data
        }
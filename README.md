# 🛡️ TradeGuide AI – Risk Intelligence Platform

> **"A Co-Pilot for Retail Traders that stops you from making emotional, money-losing decisions."**

TradeGuide AI is not just another stock predictor. It is a **Risk Intelligence Layer** that sits on top of market data to detect **Institutional Traps**, **Market Chop**, and **Time Decay Risk** in real-time. It acts as a firewall against bad trades.

![Project Status](https://img.shields.io/badge/Status-Beta-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Key Features (The "5-Pillar" Engine)

### 1. 🚦 The Risk Shield (Anti-Chop)
* **Problem:** 70% of breakouts fail because the market is sideways ("Choppy").
* **Solution:** Uses **ADX (Average Directional Index)** to detect low-momentum zones.
* **Logic:** If `ADX < 20`, the engine blocks "Buy" signals to prevent stop-loss hunting.

### 2. 🪤 Trap Detector (Fakeout Protection)
* **Problem:** Retail traders get trapped buying "fake breakouts" (High Price, Low Volume).
* **Solution:** A **Volume Divergence Algorithm** that flags price moves unsupported by volume.
* **Output:** `⚠️ TRAP DETECTED` warning on the dashboard.

### 3. 🏦 Institutional Intelligence (SMC)
* **Problem:** Support/Resistance lines are often broken by big banks to grab liquidity.
* **Solution:** Identifies **Order Blocks (OB)** and **Fair Value Gaps (FVG)** using Smart Money Concepts.
* **Output:** Highlights "Institutional Entry Zones" instead of random lines.

### 4. 📰 News Sentiment Veto
* **Problem:** Technicals lag behind breaking news.
* **Solution:** Uses **NLP (TextBlob)** to scan live headlines.
* **Logic:** If `Technicals = BUY` but `News = NEGATIVE`, the trade is **Vetoed**.

### 5. 📉 Option Decay Meter
* **Problem:** Option buyers lose money to Time Decay (Theta) even if the direction is right.
* **Solution:** Compares **Historical Volatility** vs. **Trend Strength** to warn if a trade will bleed value due to Theta.

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Data Engine:** `yfinance` (Live Market Data)
* **Analysis:** `pandas`, `numpy`, `scipy` (Statistical Modeling)
* **NLP:** `TextBlob` (Sentiment Analysis)
* **Frontend:** HTML5, CSS3 (Dark Theme), ApexCharts.js (Interactive Charts)

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/TradeGuideAI.git](https://github.com/YOUR_USERNAME/TradeGuideAI.git)
    cd TradeGuideAI
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python run.py
    ```

4.  **Open Dashboard**
    * Go to: `http://127.0.0.1:5000`
    * **Login:** Create a new user account (Data is saved locally in `instance/database.db`).

---

## 📸 Screenshots


<img width="1918" height="903" alt="risk engine page" src="https://github.com/user-attachments/assets/b9da3b25-acc4-4cad-a875-698cf47ee3b3" />

* **Risk Dashboard:** Real-time analysis of ADX, Traps, and Sentiment.


---

## 🤝 Contributing

This project is open for contributions!
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## ⚠️ Disclaimer

**Not Financial Advice.** This tool is for educational and analytical purposes only. Trading stocks and options involves high risk. Always consult a certified financial advisor before trading.

---

**Built with 💻 & ☕ by AJAY MANOJ

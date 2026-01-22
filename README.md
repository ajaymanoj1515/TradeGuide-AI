# 🛡️ TradeGuide AI: The "Risk-First" Logic Layer for Retail Traders

> **Status:** Active Development (v2.0)
> **Tech Stack:** Python, FastAPI, TA-Lib, TextBlob (NLP), HTML5/JS

### 🚨 The Problem
Most retail traders don't lose money because they can't find trades; they lose because they **force trades** in poor conditions. They trade blindly during choppy markets (sideways trends) or against institutional flow.

### 💡 The Solution
**TradeGuide AI** is not just a screener. It is a **Pre-Execution Logic Layer**. It acts as a "Safety Shield" that validates market conditions *before* a trade signal is generated.

### ⚡ Key Features

**1. The "Choppy Market" Guard (ADX Filter)**
* **Logic:** Calculates the Average Directional Index (ADX) in real-time.
* **Action:** If `ADX < 20`, the engine blocks "Trend Following" signals, preventing losses in sideways markets.

**2. Smart Money Concepts (SMC) Engine**
* **Logic:** Identifies "Order Blocks" and "Fair Value Gaps" (FVG) where institutions are likely to step in.
* **Action:** Highlights high-probability reversal zones instead of standard support/resistance.

**3. Sentiment Veto (NLP)**
* **Logic:** Scrapes live news headlines and processes them using `TextBlob` and VADER analysis.
* **Action:** If technicals say "Buy" but sentiment is "Negative," the AI vetoes the trade.

### 📸 Interface (Dark Mode)

*(Designed to match the aesthetic of modern brokerage terminals like Kite)*
<img width="1919" height="909" alt="Screenshot 2026-01-20 205821" src="https://github.com/user-attachments/assets/8c5ea9c1-5204-4ba1-9c4b-5fbcd9769e08" />

### 🚀 How to Run Locally

```bash
# 1. Clone the repo
git clone [https://github.com/ajaymanoj1515/TradeGuide-AI.git](https://github.com/ajaymanoj1515/TradeGuide-AI.git)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

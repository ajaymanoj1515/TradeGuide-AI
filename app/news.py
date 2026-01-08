import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import random

class NewsEngine:
    def __init__(self, ticker=None):
        self.ticker = ticker
        self.news_data = []

    def fetch_news(self):
        # ... (Keep your existing stock-specific logic if you have it, or use generic logic below)
        return self.fetch_general_news()

    def fetch_general_news(self, category='finance'):
        # 1. Define Search Query
        search_map = {
            'finance': 'Stock Market India',
            'crypto': 'Cryptocurrency News',
            'forex': 'Forex Trading Market',
            'economy': 'Global Economy'
        }
        query = search_map.get(category, 'Stock Market')
        
        # 2. Google News RSS URL
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        # 3. ADD HEADERS (Crucial Fix)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, features="xml")
            items = soup.findAll('item')
            
            if not items:
                raise Exception("No items found")

            self.news_data = []
            for item in items[:12]:
                title = item.title.text
                link = item.link.text
                pub_date = item.pubDate.text if item.pubDate else "Just now"
                
                # AI Sentiment Analysis
                analysis = TextBlob(title)
                score = analysis.sentiment.polarity
                
                if score > 0.1: 
                    color = "#00e676" # Green
                    sentiment = "Positive"
                elif score < -0.1: 
                    color = "#ff5252" # Red
                    sentiment = "Negative"
                else: 
                    color = "#aaa"
                    sentiment = "Neutral"
                
                self.news_data.append({
                    "title": title,
                    "link": link,
                    "published": pub_date[:16],
                    "color": color,
                    "sentiment": sentiment
                })
            return True

        except Exception as e:
            print(f"News Fetch Error: {e}")
            # FALLBACK DATA (So the page is never empty)
            self.news_data = [
                {"title": "Market hits all-time high amidst strong global cues", "link": "#", "published": "Just now", "color": "#00e676", "sentiment": "Positive"},
                {"title": "Inflation concerns rise as oil prices surge", "link": "#", "published": "1 hour ago", "color": "#ff5252", "sentiment": "Negative"},
                {"title": "Tech stocks rally ahead of quarterly earnings", "link": "#", "published": "2 hours ago", "color": "#00e676", "sentiment": "Positive"},
                {"title": "Central Bank keeps interest rates unchanged", "link": "#", "published": "Today", "color": "#aaa", "sentiment": "Neutral"},
            ]
            return False

    def get_data(self):
        return self.news_data
    
    def get_results(self):
        # Helper for the API response
        if not self.news_data:
            return None
        
        # Calculate average mood
        pos = sum(1 for n in self.news_data if n['sentiment'] == 'Positive')
        neg = sum(1 for n in self.news_data if n['sentiment'] == 'Negative')
        
        if pos > neg: return {'mood_label': 'Bullish', 'mood_color': '#00e676', 'articles': self.news_data[:3]}
        if neg > pos: return {'mood_label': 'Bearish', 'mood_color': '#ff5252', 'articles': self.news_data[:3]}
        return {'mood_label': 'Neutral', 'mood_color': '#aaa', 'articles': self.news_data[:3]}
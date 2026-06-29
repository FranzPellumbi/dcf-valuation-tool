import os
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

def get_news_sentiment(ticker, company_name):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return None

        headlines = []
        for article in news[:10]:
            try:
                title = article["content"]["title"]
                if title:
                    headlines.append(title)
            except:
                continue

        if not headlines:
            return None

        headlines_text = "\n".join([f"- {h}" for h in headlines])

        client = Groq(api_key=os.getenv("your-groq-key-here") 

        prompt = f"""You are a financial analyst. Analyze the sentiment of these recent news headlines for {company_name} ({ticker}).

Headlines:
{headlines_text}

Respond in exactly this format:
OVERALL SENTIMENT: [BULLISH/BEARISH/NEUTRAL]
SENTIMENT SCORE: [number from -10 to +10]
KEY THEMES: [2-3 bullet points of main themes]
ANALYST TAKE: [2-3 sentences on what this means for the stock]
HEADLINES ANALYZED: {len(headlines)}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )

        result = response.choices[0].message.content

        lines = result.strip().split("\n")
        sentiment = "NEUTRAL"
        score = 0

        for line in lines:
            if "OVERALL SENTIMENT:" in line:
                sentiment = line.split(":")[-1].strip()
            elif "SENTIMENT SCORE:" in line:
                try:
                    score = float(line.split(":")[-1].strip())
                except:
                    score = 0

        return {
            "sentiment": sentiment,
            "score": score,
            "full_analysis": result,
            "headlines": headlines,
            "num_headlines": len(headlines)
        }

    except Exception as e:
        return None


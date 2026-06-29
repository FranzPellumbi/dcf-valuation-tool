import yfinance as yf
import pandas as pd


def get_analyst_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info


    # Consensus target
    target_mean = info.get("targetMeanPrice", None)
    target_high = info.get("targetHighPrice", None)
    target_low = info.get("targetLowPrice", None)
    target_median = info.get("targetMedianPrice", None)
    recommendation = info.get("recommendationKey", "N/A").upper()
    num_analysts = info.get("numberOfAnalystOpinions", None)


    # Ratings breakdown
    ratings = {
        "Strong Buy": info.get("strongBuy", 0),
        "Buy": info.get("buy", 0),
        "Hold": info.get("hold", 0),
        "Sell": info.get("sell", 0),
        "Strong Sell": info.get("strongSell", 0),
    }


    return {
        "target_mean": target_mean,
        "target_high": target_high,
        "target_low": target_low,
        "target_median": target_median,
        "recommendation": recommendation,
        "num_analysts": num_analysts,
        "ratings": ratings,
    }


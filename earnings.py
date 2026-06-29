import yfinance as yf
import pandas as pd


def get_earnings_data(ticker):
    stock = yf.Ticker(ticker)


    try:
        # Earnings estimates
        earnings_est = stock.earnings_estimate
        revenue_est = stock.revenue_estimate
        eps_trend = stock.eps_trend
        earnings_history = stock.earnings_history


        return {
            "earnings_estimate": earnings_est,
            "revenue_estimate": revenue_est,
            "eps_trend": eps_trend,
            "earnings_history": earnings_history,
        }
    except:
        return None



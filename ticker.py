import yfinance as yf


def get_live_prices(tickers):
    prices = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            price = stock.fast_info["last_price"]
            change = stock.fast_info["last_price"] - stock.fast_info["previous_close"]
            pct = (change / stock.fast_info["previous_close"]) * 100
            arrow = "▲" if change >= 0 else "▼"
            color = "green" if change >= 0 else "red"
            prices.append({
                "ticker": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "pct": round(pct, 2),
                "arrow": arrow,
                "color": color
            })
        except:
            pass
    return prices



import yfinance as yf


def calculate_ddm(ticker, info, wacc):
    try:
        # Get dividend data
        dividend_rate = info.get("dividendRate", None)
        dividend_yield = info.get("dividendYield", None)
        payout_ratio = info.get("payoutRatio", None)
        earnings_growth = info.get("earningsGrowth", None)
        current_price = info.get("currentPrice", 0)


        if not dividend_rate or dividend_rate == 0:
            return {"applicable": False, "reason": "Company does not pay dividends"}


        # Gordon Growth Model: P = D1 / (r - g)
        # Use earnings growth as dividend growth, cap at wacc - 0.01
        if earnings_growth and earnings_growth > 0:
            dividend_growth = min(earnings_growth, wacc - 0.01)
        else:
            dividend_growth = 0.03  # default 3% growth


        # Next year dividend
        d1 = dividend_rate * (1 + dividend_growth)


        # DDM intrinsic value
        if wacc <= dividend_growth:
            return {"applicable": False, "reason": "WACC must be greater than dividend growth rate"}


        ddm_value = d1 / (wacc - dividend_growth)
        upside = ((ddm_value - current_price) / current_price * 100)


        return {
            "applicable": True,
            "dividend_rate": dividend_rate,
            "dividend_yield": dividend_yield,
            "payout_ratio": payout_ratio,
            "dividend_growth": dividend_growth,
            "d1": round(d1, 4),
            "ddm_value": round(ddm_value, 2),
            "current_price": current_price,
            "upside": round(upside, 2),
        }


    except Exception as e:
        return {"applicable": False, "reason": str(e)}



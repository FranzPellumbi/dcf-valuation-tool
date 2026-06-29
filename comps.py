import yfinance as yf
import pandas as pd

# Default peer groups
PEER_GROUPS = {
    "AAPL": ["MSFT", "GOOGL", "META", "AMZN", "NVDA"],
    "MSFT": ["AAPL", "GOOGL", "META", "AMZN", "NVDA"],
    "GOOGL": ["AAPL", "MSFT", "META", "AMZN", "NVDA"],
    "META": ["AAPL", "MSFT", "GOOGL", "AMZN", "SNAP"],
    "AMZN": ["AAPL", "MSFT", "GOOGL", "META", "WMT"],
    "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "TSM"],
    "AMD": ["NVDA", "INTC", "QCOM", "AVGO", "TSM"],
    "TSLA": ["GM", "F", "RIVN", "NIO", "STLA"],
    "JPM": ["BAC", "C", "WFC", "GS", "MS"],
    "GS": ["JPM", "MS", "BAC", "C", "WFC"],
}

def get_peers(ticker):
    return PEER_GROUPS.get(ticker, ["MSFT", "GOOGL", "META", "AMZN", "NVDA"])

def get_comps(ticker, peers):
    all_tickers = [ticker] + peers
    data = []

    for t in all_tickers:
        try:
            stock = yf.Ticker(t)
            info = stock.info

            market_cap = info.get("marketCap", None)
            enterprise_value = info.get("enterpriseValue", None)
            ebitda = info.get("ebitda", None)
            pe_ratio = info.get("trailingPE", None)
            price = info.get("currentPrice", None)

            ev_ebitda = round(enterprise_value / ebitda, 2) if enterprise_value and ebitda else None

            cash_flow = stock.cashflow
            if "Operating Cash Flow" in cash_flow.index and "Capital Expenditure" in cash_flow.index:
                ocf = cash_flow.loc["Operating Cash Flow"].iloc[0]
                capex = cash_flow.loc["Capital Expenditure"].iloc[0]
                fcf = ocf + capex
                p_fcf = round(market_cap / fcf, 2) if market_cap and fcf else None
            else:
                p_fcf = None

            data.append({
                "Ticker": t,
                "Price": f"${price:,.2f}" if price else "N/A",
                "Market Cap ($B)": round(market_cap / 1e9, 1) if market_cap else None,
                "EV/EBITDA": ev_ebitda,
                "P/E": round(pe_ratio, 2) if pe_ratio else None,
                "P/FCF": p_fcf,
            })
        except:
            data.append({
                "Ticker": t, "Price": "N/A", "Market Cap ($B)": None,
                "EV/EBITDA": None, "P/E": None, "P/FCF": None
            })

    return pd.DataFrame(data)

def get_implied_values(ticker, peers, income_stmt, fcf_series, shares_outstanding):
    comps_df = get_comps(ticker, peers)
    peer_df = comps_df[comps_df["Ticker"] != ticker]

    avg_ev_ebitda = peer_df["EV/EBITDA"].dropna().mean()
    avg_pe = peer_df["P/E"].dropna().mean()
    avg_p_fcf = peer_df["P/FCF"].dropna().mean()

    # Get subject company metrics
    ebitda = income_stmt.loc["EBITDA"].iloc[0] if "EBITDA" in income_stmt.index else None
    net_income = income_stmt.loc["Net Income"].iloc[0] if "Net Income" in income_stmt.index else None
    latest_fcf = fcf_series.iloc[0] if not fcf_series.empty else None

    implied_ev_ebitda = round((avg_ev_ebitda * ebitda) / shares_outstanding, 2) if avg_ev_ebitda and ebitda else None
    implied_pe = round((avg_pe * net_income) / shares_outstanding, 2) if avg_pe and net_income else None
    implied_p_fcf = round((avg_p_fcf * latest_fcf) / shares_outstanding, 2) if avg_p_fcf and latest_fcf else None

    return comps_df, implied_ev_ebitda, implied_pe, implied_p_fcf, avg_ev_ebitda, avg_pe, avg_p_fcf


import yfinance as yf
import pandas as pd
from dcf import calculate_fcf, calculate_wacc, extract_historical_metrics, project_fcf_detailed, calculate_dcf_full

def screen_tickers(tickers, growth_rate, terminal_growth, exit_multiple):
    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            income_stmt = stock.financials
            cash_flow = stock.cashflow
            balance_sheet = stock.get_balance_sheet()
            info = stock.info

            current_price = info.get("currentPrice", 0)
            if not current_price:
                continue

            fcf = calculate_fcf(cash_flow)
            wacc, _ = calculate_wacc(info, balance_sheet, income_stmt)
            hist_metrics = extract_historical_metrics(income_stmt, cash_flow, balance_sheet)

            proj_df, projected_fcf_list, projected_ebitda_final = project_fcf_detailed(
                hist_metrics, growth_rate, terminal_growth
            )

            dcf_results = calculate_dcf_full(
                projected_fcf_list, projected_ebitda_final, wacc, terminal_growth, exit_multiple
            )

            shares_outstanding = info.get("sharesOutstanding", 1)
            iv_midpoint = dcf_results["total_pv_midpoint"] / shares_outstanding
            upside = ((iv_midpoint - current_price) / current_price * 100)

            results.append({
                "Ticker": ticker,
                "Company": info.get("longName", ticker),
                "Current Price": round(current_price, 2),
                "Intrinsic Value": round(iv_midpoint, 2),
                "Upside/Downside (%)": round(upside, 1),
                "WACC (%)": round(wacc * 100, 2),
                "Market Cap ($B)": round(info.get("marketCap", 0) / 1e9, 1),
                "P/E": round(info.get("trailingPE", 0), 1) if info.get("trailingPE") else "N/A",
                "Sector": info.get("sector", "N/A"),
            })

        except Exception as e:
            results.append({
                "Ticker": ticker,
                "Company": ticker,
                "Current Price": "Error",
                "Intrinsic Value": "Error",
                "Upside/Downside (%)": None,
                "WACC (%)": None,
                "Market Cap ($B)": None,
                "P/E": None,
                "Sector": "Error",
            })

    df = pd.DataFrame(results)
    if "Upside/Downside (%)" in df.columns:
        df = df.sort_values("Upside/Downside (%)", ascending=False)
    return df


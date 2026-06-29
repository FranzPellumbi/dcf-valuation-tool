def get_ratios(info, balance_sheet, income_stmt, cash_flow):
    ratios = {}


    # --- Profitability ---
    ratios["Gross Margin"] = info.get("grossMargins", None)
    ratios["Operating Margin"] = info.get("operatingMargins", None)
    ratios["Net Margin"] = info.get("profitMargins", None)
    ratios["ROE"] = info.get("returnOnEquity", None)
    ratios["ROA"] = info.get("returnOnAssets", None)


    # --- Liquidity ---
    ratios["Current Ratio"] = info.get("currentRatio", None)
    ratios["Quick Ratio"] = info.get("quickRatio", None)


    # --- Leverage ---
    ratios["Debt/Equity"] = info.get("debtToEquity", None)


    # Interest Coverage — try multiple label names
    ratios["Interest Coverage"] = None
    try:
        ebit = income_stmt.loc["EBIT"].iloc[0]
        interest = None
        for label in ["Interest Expense", "Interest Expense Non Operating", "Net Interest Income"]:
            if label in income_stmt.index:
                val = income_stmt.loc[label].iloc[0]
                if val and val != 0:
                    interest = val
                    break
        if interest:
            ratios["Interest Coverage"] = round(abs(ebit / interest), 2)
    except:
        pass


    # --- Valuation ---
    ratios["P/E"] = info.get("trailingPE", None)
    ratios["Forward P/E"] = info.get("forwardPE", None)
    ratios["P/B"] = info.get("priceToBook", None)
    ratios["EV/EBITDA"] = info.get("enterpriseToEbitda", None)
    ratios["EV/Revenue"] = info.get("enterpriseToRevenue", None)


    # --- Growth ---
    ratios["Revenue Growth (YoY)"] = info.get("revenueGrowth", None)
    ratios["Earnings Growth (YoY)"] = info.get("earningsGrowth", None)


    return ratios



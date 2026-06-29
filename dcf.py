import yfinance as yf
import pandas as pd
import numpy as np


# ── 1. Fetch financials ────────────────────────────────────────────────────────
def get_financials(ticker):
    stock = yf.Ticker(ticker)
    income_stmt = stock.financials
    cash_flow = stock.cashflow
    balance_sheet = stock.get_balance_sheet()
    info = stock.info
    return income_stmt, cash_flow, balance_sheet, info


# ── 2. Historical FCF (simple method, used for sensitivity/Monte Carlo) ────────
def calculate_fcf(cash_flow):
    ocf = cash_flow.loc["Operating Cash Flow"]
    capex = cash_flow.loc["Capital Expenditure"]
    fcf = ocf + capex
    return fcf.dropna()


# ── 3. WACC — improved with live Rf, actual cost of debt, effective tax rate ──
def calculate_wacc(info, balance_sheet, income_stmt):
    # Live risk-free rate from 10-year treasury
    try:
        treasury = yf.Ticker("^TNX")
        rf = treasury.info.get("regularMarketPrice", 4.3) / 100
    except:
        rf = 0.043


    # Beta and cost of equity (CAPM)
    beta = float(info.get("beta") or 1.0)
    market_premium = 0.055
    cost_of_equity = rf + beta * market_premium


    # Effective tax rate from actual financials
    try:
        tax = float(income_stmt.loc["Tax Provision"].iloc[0])
        pretax = float(income_stmt.loc["Pretax Income"].iloc[0])
        effective_tax_rate = max(min(tax / pretax, 0.40), 0.05) if pretax > 0 else 0.21
    except:
        effective_tax_rate = 0.21


    # Cost of debt from actual interest expense / total debt
    try:
        interest_expense = None
        for label in ["Interest Expense", "Interest Expense Non Operating"]:
            if label in income_stmt.index:
                val = float(income_stmt.loc[label].iloc[0])
                if pd.notna(val) and val != 0:
                    interest_expense = abs(val)
                    break
        total_debt = float(balance_sheet.loc["TotalDebt"].iloc[0]) if "TotalDebt" in balance_sheet.index else 0
        cost_of_debt_pretax = (interest_expense / total_debt) if (interest_expense and total_debt > 0) else 0.04
        cost_of_debt_pretax = max(min(cost_of_debt_pretax, 0.15), 0.01)
    except:
        cost_of_debt_pretax = 0.04
        total_debt = 0


    cost_of_debt = cost_of_debt_pretax * (1 - effective_tax_rate)


    # Capital structure weights
    market_cap = float(info.get("marketCap") or 1)
    try:
        debt = float(balance_sheet.loc["TotalDebt"].iloc[0]) if "TotalDebt" in balance_sheet.index else 0
    except:
        debt = 0
    total_capital = market_cap + debt
    weight_equity = market_cap / total_capital
    weight_debt = debt / total_capital


    wacc = round((weight_equity * cost_of_equity) + (weight_debt * cost_of_debt), 4)


    breakdown = {
        "risk_free_rate": rf,
        "beta": beta,
        "market_premium": market_premium,
        "cost_of_equity": cost_of_equity,
        "cost_of_debt_pretax": cost_of_debt_pretax,
        "effective_tax_rate": effective_tax_rate,
        "cost_of_debt_aftertax": cost_of_debt,
        "weight_equity": weight_equity,
        "weight_debt": weight_debt,
        "wacc": wacc,
    }


    return wacc, breakdown


# ── 4. Extract historical metrics for projection assumptions ───────────────────
def extract_historical_metrics(income_stmt, cash_flow, balance_sheet):
    try:
        revenues = income_stmt.loc["Total Revenue"].dropna().values.astype(float)
        base_revenue = revenues[0]


        gross_profits = income_stmt.loc["Gross Profit"].dropna().values.astype(float)
        gross_margin = np.mean(gross_profits[:len(revenues)] / revenues[:len(gross_profits)])


        ebit_vals = None
        for label in ["EBIT", "Operating Income"]:
            if label in income_stmt.index:
                ebit_vals = income_stmt.loc[label].dropna().values.astype(float)
                break
        ebit_margin = np.mean(ebit_vals[:len(revenues)] / revenues[:len(ebit_vals)]) if ebit_vals is not None else 0.20


        try:
            tax = float(income_stmt.loc["Tax Provision"].iloc[0])
            pretax = float(income_stmt.loc["Pretax Income"].iloc[0])
            effective_tax_rate = max(min(tax / pretax, 0.40), 0.05) if pretax > 0 else 0.21
        except:
            effective_tax_rate = 0.21


        da_pct = 0.03
        for label in ["Reconciled Depreciation", "Depreciation And Amortization"]:
            if label in cash_flow.index:
                da_vals = cash_flow.loc[label].dropna().values.astype(float)
                da_pct = np.mean(abs(da_vals[:len(revenues)]) / revenues[:len(da_vals)])
                break


        capex_pct = 0.04
        if "Capital Expenditure" in cash_flow.index:
            capex_vals = cash_flow.loc["Capital Expenditure"].dropna().values.astype(float)
            capex_pct = np.mean(abs(capex_vals[:len(revenues)]) / revenues[:len(capex_vals)])


        nwc_pct = 0.05
        try:
            ca = balance_sheet.loc["Current Assets"].values.astype(float) if "Current Assets" in balance_sheet.index else None
            cl = balance_sheet.loc["Current Liabilities"].values.astype(float) if "Current Liabilities" in balance_sheet.index else None
            if ca is not None and cl is not None:
                nwc = ca - cl
                nwc_pct = np.mean(nwc[:len(revenues)] / revenues[:len(nwc)])
        except:
            pass


       # Revenue growth
        if len(revenues) >= 2:
            revenue_growth = float((revenues[0] - revenues[-1]) / revenues[-1]) / max(len(revenues) - 1, 1)
        else:
            revenue_growth = 0.05

        return {
            "base_revenue": base_revenue,
            "gross_margin": gross_margin,
            "ebit_margin": ebit_margin,
            "effective_tax_rate": effective_tax_rate,
            "da_pct": da_pct,
            "capex_pct": capex_pct,
            "nwc_pct": nwc_pct,
            "revenue_growth": revenue_growth,
        }
    except:
        return {
            "base_revenue": 100e9, "gross_margin": 0.40, "ebit_margin": 0.20,
            "effective_tax_rate": 0.21, "da_pct": 0.03, "capex_pct": 0.04, "nwc_pct": 0.05, "revenue_growth" : 0.05
        }


# ── 5. Full 3-statement FCF projection ────────────────────────────────────────
def project_fcf_detailed(metrics, growth_rate, terminal_growth, years=5):
    """
    Revenue → COGS → Gross Profit → EBIT → NOPAT + D&A - CapEx - ΔNWC = FCF
    Growth rate fades from growth_rate to terminal_growth over projection period
    """
    base_revenue = metrics["base_revenue"]
    gross_margin = metrics["gross_margin"]
    ebit_margin = metrics["ebit_margin"]
    tax_rate = metrics["effective_tax_rate"]
    da_pct = metrics["da_pct"]
    capex_pct = metrics["capex_pct"]
    nwc_pct = metrics["nwc_pct"]


    projections = []
    prev_revenue = base_revenue
    prev_nwc = base_revenue * nwc_pct


    for year in range(1, years + 1):
        # Growth fades linearly from growth_rate to terminal_growth
        fade = (year - 1) / max(years - 1, 1)
        year_growth = growth_rate * (1 - fade) + terminal_growth * fade


        revenue = prev_revenue * (1 + year_growth)
        gross_profit = revenue * gross_margin
        ebit = revenue * ebit_margin
        nopat = ebit * (1 - tax_rate)
        da = revenue * da_pct
        capex = revenue * capex_pct
        nwc = revenue * nwc_pct
        delta_nwc = nwc - prev_nwc
        fcf = nopat + da - capex - delta_nwc
        ebitda = ebit + da


        projections.append({
            "Year": f"Year {year}",
            "Revenue ($B)": round(revenue / 1e9, 2),
            "Gross Profit ($B)": round(gross_profit / 1e9, 2),
            "EBIT ($B)": round(ebit / 1e9, 2),
            "NOPAT ($B)": round(nopat / 1e9, 2),
            "D&A ($B)": round(da / 1e9, 2),
            "CapEx ($B)": round(capex / 1e9, 2),
            "ΔNWC ($B)": round(delta_nwc / 1e9, 2),
            "FCF ($B)": round(fcf / 1e9, 2),
            "_fcf_raw": fcf,
            "_ebitda_raw": ebitda,
        })


        prev_revenue = revenue
        prev_nwc = nwc


    proj_df = pd.DataFrame(projections)
    projected_fcf_list = proj_df["_fcf_raw"].tolist()
    projected_ebitda_final = float(proj_df["_ebitda_raw"].iloc[-1])


    return proj_df, projected_fcf_list, projected_ebitda_final


# ── 6. DCF with both terminal value methods ────────────────────────────────────
def calculate_dcf_full(projected_fcf_list, projected_ebitda_final, wacc, terminal_growth, exit_multiple=12):
    years = len(projected_fcf_list)


    pv_fcf = [cf / (1 + wacc) ** (i + 1) for i, cf in enumerate(projected_fcf_list)]
    sum_pv_fcf = sum(pv_fcf)


    # Method 1: Perpetuity growth (Gordon Growth Model)
    tv_perpetuity = projected_fcf_list[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_tv_perpetuity = tv_perpetuity / (1 + wacc) ** years
    total_pv_perpetuity = sum_pv_fcf + pv_tv_perpetuity


    # Method 2: Exit multiple (EV/EBITDA)
    tv_multiple = projected_ebitda_final * exit_multiple
    pv_tv_multiple = tv_multiple / (1 + wacc) ** years
    total_pv_multiple = sum_pv_fcf + pv_tv_multiple


    # Midpoint
    total_pv_midpoint = (total_pv_perpetuity + total_pv_multiple) / 2


    return {
        "pv_fcf_list": pv_fcf,
        "sum_pv_fcf": sum_pv_fcf,
        "tv_perpetuity": tv_perpetuity,
        "pv_tv_perpetuity": pv_tv_perpetuity,
        "total_pv_perpetuity": total_pv_perpetuity,
        "tv_multiple": tv_multiple,
        "pv_tv_multiple": pv_tv_multiple,
        "total_pv_multiple": total_pv_multiple,
        "total_pv_midpoint": total_pv_midpoint,
        "exit_multiple": exit_multiple,
    }


# ── 7. Keep simple DCF for sensitivity analysis / Monte Carlo ──────────────────
def calculate_dcf(fcf, wacc, growth_rate=0.05, terminal_growth=0.025, years=5):
    base_fcf = fcf.mean()
    projected_fcf = [base_fcf * (1 + growth_rate) ** y for y in range(1, years + 1)]
    pv_fcf = [cf / (1 + wacc) ** (i + 1) for i, cf in enumerate(projected_fcf)]
    terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** years
    total_pv = sum(pv_fcf) + pv_terminal
    return total_pv, projected_fcf, pv_fcf, pv_terminal


# ── 8. Sensitivity analysis ────────────────────────────────────────────────────
def sensitivity_analysis(fcf, wacc, growth_rate, terminal_growth):
    wacc_range = [wacc - 0.02, wacc - 0.01, wacc, wacc + 0.01, wacc + 0.02]
    tg_range = [terminal_growth - 0.01, terminal_growth - 0.005, terminal_growth,
                terminal_growth + 0.005, terminal_growth + 0.01]
    results = {}
    for w in wacc_range:
        row = {}
        for tg in tg_range:
            if w > tg:
                total_pv, _, _, _ = calculate_dcf(fcf, w, growth_rate, tg)
                row[f"{tg*100:.1f}%"] = round(total_pv / 1e9, 2)
        results[f"{w*100:.1f}%"] = row
    return pd.DataFrame(results).T



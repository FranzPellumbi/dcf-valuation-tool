import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


def generate_ai_report(ticker, company_name, current_price, iv_midpoint, iv_perpetuity,
                        iv_multiple, wacc, growth_rate, terminal_growth, ratios,
                        comps_df, analyst_data, hist_metrics, proj_df, mc_results,
                        insider_summary, info):


    client = Groq(api_key=os.getenv("GROQ_API_KEY"))


    upside = ((iv_midpoint - current_price) / current_price * 100)
    if upside > 15:
        recommendation = "BUY"
    elif upside < -15:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"


    # Build data context
    context = f"""
You are a senior equity research analyst at a top investment bank. Write a professional, detailed equity research report for {company_name} ({ticker}).


Use ONLY the data provided below. Write like a real sell-side analyst — confident, data-driven, and insightful.


=== VALUATION DATA ===
Current Price: ${current_price:,.2f}
DCF Intrinsic Value (Midpoint): ${iv_midpoint:,.2f}
DCF Intrinsic Value (Perpetuity): ${iv_perpetuity:,.2f}
DCF Intrinsic Value (Exit Multiple): ${iv_multiple:,.2f}
Upside/Downside: {upside:,.1f}%
Recommendation: {recommendation}
WACC: {wacc*100:.2f}%
FCF Growth Rate (Year 1): {growth_rate*100:.1f}%
Terminal Growth Rate: {terminal_growth*100:.1f}%


=== COMPANY INFO ===
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Market Cap: ${info.get('marketCap', 0)/1e9:,.1f}B
Revenue (TTM): ${info.get('totalRevenue', 0)/1e9:,.1f}B
Business Summary: {info.get('longBusinessSummary', 'N/A')[:500]}


=== FINANCIAL RATIOS ===
Gross Margin: {ratios.get('Gross Margin', 0)*100:.1f}% 
Operating Margin: {ratios.get('Operating Margin', 0)*100:.1f}%
Net Margin: {ratios.get('Net Margin', 0)*100:.1f}%
ROE: {ratios.get('ROE', 0)*100:.1f}%
ROA: {ratios.get('ROA', 0)*100:.1f}%
Current Ratio: {ratios.get('Current Ratio', 'N/A')}
Debt/Equity: {ratios.get('Debt/Equity', 'N/A')}
P/E: {ratios.get('P/E', 'N/A')}
Forward P/E: {ratios.get('Forward P/E', 'N/A')}
EV/EBITDA: {ratios.get('EV/EBITDA', 'N/A')}
Revenue Growth YoY: {ratios.get('Revenue Growth (YoY)', 0)*100:.1f}%
Earnings Growth YoY: {ratios.get('Earnings Growth (YoY)', 0)*100:.1f}%


=== HISTORICAL METRICS ===
Gross Margin (hist avg): {hist_metrics['gross_margin']*100:.1f}%
EBIT Margin (hist avg): {hist_metrics['ebit_margin']*100:.1f}%
CapEx % Revenue: {hist_metrics['capex_pct']*100:.1f}%


=== FCF PROJECTION ===
{proj_df[['Year', 'Revenue ($B)', 'EBIT ($B)', 'FCF ($B)']].to_string(index=False)}


=== ANALYST CONSENSUS ===
Recommendation: {analyst_data.get('recommendation', 'N/A')}
Mean Price Target: ${analyst_data.get('target_mean', 0):,.2f}
High Target: ${analyst_data.get('target_high', 0):,.2f}
Low Target: ${analyst_data.get('target_low', 0):,.2f}
Number of Analysts: {analyst_data.get('num_analysts', 'N/A')}


=== MONTE CARLO ===
5th Percentile (Bear): ${mc_results.quantile(0.05):,.2f}
50th Percentile (Base): ${mc_results.quantile(0.50):,.2f}
95th Percentile (Bull): ${mc_results.quantile(0.95):,.2f}
Probability Overvalued: {(mc_results < current_price).mean()*100:.1f}%


=== INSIDER ACTIVITY ===
{f"Total Buys: {insider_summary['total_buys']:,} shares, Total Sells: {insider_summary['total_sells']:,} shares, Sentiment: {insider_summary['sentiment']}" if insider_summary else "No insider data available"}


=== COMPARABLE COMPANIES ===
{comps_df[['Ticker', 'EV/EBITDA', 'P/E', 'P/FCF']].to_string(index=False)}


Write the report in the following exact structure:


# {company_name} ({ticker}) — Equity Research Report
**{recommendation}** | Price Target: $[calculate a price target] | Current Price: ${current_price:,.2f}


## Executive Summary
[2-3 paragraphs covering investment thesis, key metrics, and recommendation rationale]


## Company Overview
[1-2 paragraphs on business model and industry position]


## Investment Thesis
[3 bullet points with detailed explanations of key bull case drivers]


## Financial Analysis
[2-3 paragraphs analyzing revenue trends, margins, FCF quality, and balance sheet]


## Valuation
[2 paragraphs covering DCF methodology, assumptions, and comps comparison]


## Risk Factors
[3 bullet points covering key downside risks]


## Recommendation & Price Target
[1 paragraph with final recommendation, price target, and upside/downside]
"""


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": context}],
        max_tokens=4000,
        temperature=0.7
    )


    return response.choices[0].message.content



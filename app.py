import streamlit as st
import plotly.graph_objects as go
from dcf import (get_financials, calculate_fcf, calculate_wacc,
                 extract_historical_metrics, project_fcf_detailed,
                 calculate_dcf_full, calculate_dcf, sensitivity_analysis)
from report import generate_report
from monte_carlo import run_monte_carlo
from comps import get_peers, get_implied_values
from excel_export import generate_excel
from football_field import build_football_field
from ratios import get_ratios
from analyst import get_analyst_data
from ddm import calculate_ddm
from earnings import get_earnings_data
from insider import get_insider_trades, get_insider_summary
from ticker import get_live_prices
from ai_report import generate_ai_report
from scenarios import run_scenarios
from screener import screen_tickers 



# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="DCF Valuation Tool", page_icon="📊", layout="wide")
st.markdown("""
<style>
    .stMetric { background-color: #1c1f2e; border-radius: 8px; padding: 15px; border: 1px solid #2d3250; }
    .stMetric label { color: #8892b0 !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 📊 DCF Valuation Tool")
st.markdown("*Institutional-grade intrinsic value analysis*")
st.markdown("---")

# ── Live ticker bar ────────────────────────────────────────────────────────────
market_tickers = ["SPY", "QQQ", "DIA", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "JPM"]
prices = get_live_prices(market_tickers)


ticker_html = '<div style="background:#1c1f2e; padding:10px; border-radius:8px; display:flex; gap:30px; overflow-x:auto; border:1px solid #2d3250;">'
for p in prices:
    color = "#00b386" if p["color"] == "green" else "#ff6b6b"
    ticker_html += f'''
        <div style="text-align:center; min-width:80px;">
            <div style="color:#8892b0; font-size:11px;">{p["ticker"]}</div>
            <div style="color:white; font-size:14px; font-weight:bold;">${p["price"]}</div>
            <div style="color:{color}; font-size:11px;">{p["arrow"]} {p["pct"]}%</div>
        </div>'''
ticker_html += '</div>'


st.markdown(ticker_html, unsafe_allow_html=True)
st.markdown("---")


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Inputs")
    ticker = st.text_input("Ticker Symbol", value="AAPL", placeholder="e.g. AAPL").upper()
    st.markdown("---")
    st.markdown("### DCF Assumptions")
    growth_rate_pct = st.slider("FCF Growth Rate (Year 1)", 1, 20, 8, 1, format="%d%%")
    growth_rate = growth_rate_pct / 100
    terminal_growth_pct = st.slider("Terminal Growth Rate", 1, 5, 2, 1, format="%d%%")
    terminal_growth = terminal_growth_pct / 100
    exit_multiple = st.slider("Exit EV/EBITDA Multiple", 6, 20, 12, 1, format="%dx")
    st.markdown("---")
    run = st.button("Run Analysis", use_container_width=True)


# ── Run analysis ───────────────────────────────────────────────────────────────
if ticker and run:
    with st.spinner(f"Fetching financials for {ticker}..."):
        income_stmt, cash_flow, balance_sheet, info = get_financials(ticker)
        fcf = calculate_fcf(cash_flow)
        wacc, wacc_breakdown = calculate_wacc(info, balance_sheet, income_stmt)
        hist_metrics = extract_historical_metrics(income_stmt, cash_flow, balance_sheet)

    shares_outstanding = info.get("sharesOutstanding", 1)
    current_price = info.get("currentPrice", 0)
    company_name = info.get("longName", ticker)

    scenarios = run_scenarios(
        hist_metrics, wacc, terminal_growth, exit_multiple, shares_outstanding
    )


    with st.spinner("Building FCF model..."):
        proj_df, projected_fcf_list, projected_ebitda_final = project_fcf_detailed(
            hist_metrics, growth_rate, terminal_growth
        )
        dcf_results = calculate_dcf_full(
            projected_fcf_list, projected_ebitda_final, wacc, terminal_growth, exit_multiple
        )


    shares_outstanding = info.get("sharesOutstanding", 1)
    current_price = info.get("currentPrice", 0)
    company_name = info.get("longName", ticker)


    iv_perpetuity = dcf_results["total_pv_perpetuity"] / shares_outstanding
    iv_multiple = dcf_results["total_pv_multiple"] / shares_outstanding
    iv_midpoint = dcf_results["total_pv_midpoint"] / shares_outstanding


    with st.spinner("Running Monte Carlo..."):
        mc_results = run_monte_carlo(fcf, wacc, growth_rate, terminal_growth, shares_outstanding)


    with st.spinner("Fetching peer data..."):
        peers = get_peers(ticker)
        comps_df, implied_ev_ebitda, implied_pe, implied_p_fcf, avg_ev_ebitda, avg_pe, avg_p_fcf = get_implied_values(
            ticker, peers, income_stmt, fcf, shares_outstanding
        )


    analyst_data = get_analyst_data(ticker)
    insider_df = get_insider_trades(ticker)
    insider_summary = get_insider_summary(ticker)
    earnings_data = get_earnings_data(ticker)
    ddm_data = calculate_ddm(ticker, info, wacc)


    pdf_filename = generate_report(ticker, current_price, iv_midpoint, wacc, growth_rate, terminal_growth, fcf, projected_fcf_list)
    excel_filename = generate_excel(ticker, current_price, iv_midpoint, wacc, growth_rate, terminal_growth, fcf, projected_fcf_list, comps_df, mc_results)


    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()
    with open(excel_filename, "rb") as f:
        excel_bytes = f.read()


    st.session_state.data = {
        "ticker": ticker, "company_name": company_name,
        "current_price": current_price, "shares_outstanding": shares_outstanding,
        "info": info, "income_stmt": income_stmt, "cash_flow": cash_flow,
        "balance_sheet": balance_sheet, "fcf": fcf,
        "wacc": wacc, "wacc_breakdown": wacc_breakdown,
        "hist_metrics": hist_metrics,
        "proj_df": proj_df, "projected_fcf_list": projected_fcf_list,
        "dcf_results": dcf_results,
        "iv_perpetuity": iv_perpetuity, "iv_multiple": iv_multiple, "iv_midpoint": iv_midpoint,
        "growth_rate": growth_rate, "terminal_growth": terminal_growth, "exit_multiple": exit_multiple,
        "mc_results": mc_results,
        "comps_df": comps_df, "implied_ev_ebitda": implied_ev_ebitda,
        "implied_pe": implied_pe, "implied_p_fcf": implied_p_fcf,
        "avg_ev_ebitda": avg_ev_ebitda, "avg_pe": avg_pe, "avg_p_fcf": avg_p_fcf,
        "ratios": get_ratios(info, balance_sheet, income_stmt, cash_flow),
        "analyst_data": analyst_data,
        "insider_df": insider_df, "insider_summary": insider_summary,
        "earnings_data": earnings_data, "ddm_data": ddm_data,
        "pdf_bytes": pdf_bytes, "pdf_filename": pdf_filename,
        "excel_bytes": excel_bytes, "excel_filename": excel_filename,
        "scenarios": scenarios, 
        
    }


# ── Display ────────────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.stop()


d = st.session_state.data


# ── 1. Company overview ────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 4])
with col2:
    st.markdown(f"## {d['company_name']} ({d['ticker']})")
    st.markdown(f"*{d['info'].get('sector','')} | {d['info'].get('industry','')} | {d['info'].get('country','')}*")


col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Market Cap", f"${d['info'].get('marketCap',0)/1e12:,.2f}T")
col2.metric("Revenue (TTM)", f"${d['info'].get('totalRevenue',0)/1e9:,.0f}B")
col3.metric("Net Margin", f"{d['info'].get('profitMargins',0)*100:.1f}%")
col4.metric("52W High", f"${d['info'].get('fiftyTwoWeekHigh',0):,.2f}")
col5.metric("52W Low", f"${d['info'].get('fiftyTwoWeekLow',0):,.2f}")


with st.expander("Company Description"):
    st.write(d['info'].get("longBusinessSummary", "No description available."))
st.markdown("---")


# ── 2. Financial ratios ────────────────────────────────────────────────────────
st.markdown("### Financial Ratios")
r = d['ratios']
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**Profitability**")
    st.metric("Gross Margin", f"{r['Gross Margin']*100:.1f}%" if r['Gross Margin'] else "N/A")
    st.metric("Operating Margin", f"{r['Operating Margin']*100:.1f}%" if r['Operating Margin'] else "N/A")
    st.metric("Net Margin", f"{r['Net Margin']*100:.1f}%" if r['Net Margin'] else "N/A")
    st.metric("ROE", f"{r['ROE']*100:.1f}%" if r['ROE'] else "N/A")
    st.metric("ROA", f"{r['ROA']*100:.1f}%" if r['ROA'] else "N/A")
with col2:
    st.markdown("**Liquidity & Leverage**")
    st.metric("Current Ratio", f"{r['Current Ratio']:.2f}x" if r['Current Ratio'] else "N/A")
    st.metric("Quick Ratio", f"{r['Quick Ratio']:.2f}x" if r['Quick Ratio'] else "N/A")
    st.metric("Debt/Equity", f"{r['Debt/Equity']:.1f}%" if r['Debt/Equity'] else "N/A")
    st.metric("Interest Coverage", f"{r['Interest Coverage']:.1f}x" if r['Interest Coverage'] else "N/A")
with col3:
    st.markdown("**Valuation Multiples**")
    st.metric("P/E (TTM)", f"{r['P/E']:.1f}x" if r['P/E'] else "N/A")
    st.metric("Forward P/E", f"{r['Forward P/E']:.1f}x" if r['Forward P/E'] else "N/A")
    st.metric("P/B", f"{r['P/B']:.1f}x" if r['P/B'] else "N/A")
    st.metric("EV/EBITDA", f"{r['EV/EBITDA']:.1f}x" if r['EV/EBITDA'] else "N/A")
    st.metric("EV/Revenue", f"{r['EV/Revenue']:.1f}x" if r['EV/Revenue'] else "N/A")
with col4:
    st.markdown("**Growth**")
    st.metric("Revenue Growth", f"{r['Revenue Growth (YoY)']*100:.1f}%" if r['Revenue Growth (YoY)'] else "N/A")
    st.metric("Earnings Growth", f"{r['Earnings Growth (YoY)']*100:.1f}%" if r['Earnings Growth (YoY)'] else "N/A")
st.markdown("---")


# ── 3. WACC breakdown ──────────────────────────────────────────────────────────
st.markdown("### WACC Breakdown")
wb = d['wacc_breakdown']
col1, col2, col3, col4 = st.columns(4)
col1.metric("WACC", f"{wb['wacc']*100:.2f}%")
col2.metric("Cost of Equity", f"{wb['cost_of_equity']*100:.2f}%")
col3.metric("Cost of Debt (after-tax)", f"{wb['cost_of_debt_aftertax']*100:.2f}%")
col4.metric("Effective Tax Rate", f"{wb['effective_tax_rate']*100:.1f}%")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Risk-Free Rate (live)", f"{wb['risk_free_rate']*100:.2f}%")
col2.metric("Beta", f"{wb['beta']:.2f}")
col3.metric("Equity Weight", f"{wb['weight_equity']*100:.1f}%")
col4.metric("Debt Weight", f"{wb['weight_debt']*100:.1f}%")
st.markdown("---")


# ── 4. Valuation summary ───────────────────────────────────────────────────────
st.markdown("### Valuation Summary")
cp = d['current_price']
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"${cp:,.2f}")
col2.metric("DCF — Perpetuity", f"${d['iv_perpetuity']:,.2f}", delta=f"{((d['iv_perpetuity']-cp)/cp*100):,.1f}%")
col3.metric("DCF — Exit Multiple", f"${d['iv_multiple']:,.2f}", delta=f"{((d['iv_multiple']-cp)/cp*100):,.1f}%")
col4.metric("DCF — Midpoint", f"${d['iv_midpoint']:,.2f}", delta=f"{((d['iv_midpoint']-cp)/cp*100):,.1f}%")


dcf = d['dcf_results']
col1, col2, col3 = st.columns(3)
col1.metric("TV — Perpetuity", f"${dcf['tv_perpetuity']/1e9:,.1f}B", f"Exit Multiple: {d['exit_multiple']}x")
col2.metric("TV — Exit Multiple", f"${dcf['tv_multiple']/1e9:,.1f}B")
col3.metric("PV of FCFs", f"${dcf['sum_pv_fcf']/1e9:,.1f}B")
st.markdown("---")

col3.metric("PV of FCFs", f"${dcf['sum_pv_fcf']/1e9:,.1f}B")
st.markdown("---")

# ── Scenarios ──────────────────────────────────────────────────────────────────
st.markdown("### 🎯 Bull / Base / Bear Scenarios")
st.caption("Three DCF scenarios with varying margin, growth, and WACC assumptions")

scenarios = d['scenarios']
col1, col2, col3 = st.columns(3)

for col, case in zip([col1, col2, col3], ['bear', 'base', 'bull']):
    s = scenarios[case]
    upside = ((s['iv'] - d['current_price']) / d['current_price'] * 100)
    with col:
        st.markdown(f"#### {s['label']}")
        st.metric("Intrinsic Value", f"${s['iv']:,.2f}", delta=f"{upside:,.1f}%")
        st.markdown(f"**WACC:** {s['wacc']}%")
        st.markdown(f"**Revenue Growth:** {s['growth']}%")
        st.markdown(f"**Terminal Growth:** {s['terminal']}%")
        st.markdown(f"**EBIT Margin:** {s['ebit_margin']}%")
        st.markdown(f"**Exit Multiple:** {s['exit_multiple']}x")

fig_scenarios = go.Figure()
cases = ['Bear Case', 'Base Case', 'Bull Case']
values = [scenarios['bear']['iv'], scenarios['base']['iv'], scenarios['bull']['iv']]
colors = ['#ff6b6b', '#4a9eff', '#00b386']

for case, value, color in zip(cases, values, colors):
    fig_scenarios.add_trace(go.Bar(
        name=case, x=[case], y=[value],
        marker_color=color, text=f"${value:,.2f}",
        textposition='outside'
    ))

fig_scenarios.add_hline(
    y=d['current_price'], line_color="white",
    line_dash="dash", annotation_text=f"Current: ${d['current_price']:,.2f}",
    annotation_font_color="white"
)
fig_scenarios.update_layout(
    plot_bgcolor="#1c1f2e", paper_bgcolor="#0e1117", font_color="#ccd6f6",
    title="Intrinsic Value by Scenario vs Current Price",
    yaxis_title="Value Per Share ($)", showlegend=False, height=400
)
st.plotly_chart(fig_scenarios, use_container_width=True)
st.markdown("---")


# ── 5. Analyst price targets ───────────────────────────────────────────────────
st.markdown("### Analyst Price Targets")
a = d['analyst_data']
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Consensus", a['recommendation'])
col2.metric("Mean Target", f"${a['target_mean']:,.2f}" if a['target_mean'] else "N/A")
col3.metric("Median Target", f"${a['target_median']:,.2f}" if a['target_median'] else "N/A")
col4.metric("High Target", f"${a['target_high']:,.2f}" if a['target_high'] else "N/A")
col5.metric("Low Target", f"${a['target_low']:,.2f}" if a['target_low'] else "N/A")
if a['num_analysts']:
    st.caption(f"Based on {a['num_analysts']} analyst opinions")
ratings = a['ratings']
total = sum(ratings.values())
if total > 0:
    fig_ratings = go.Figure()
    colors = ["#00b386", "#4a9eff", "#ffd700", "#ff6b6b", "#cc0000"]
    for (label, count), color in zip(ratings.items(), colors):
        fig_ratings.add_trace(go.Bar(name=label, x=[count], y=["Ratings"], orientation="h",
                                      marker_color=color, text=f"{label}: {count}", textposition="inside"))
    fig_ratings.update_layout(barmode="stack", plot_bgcolor="#1c1f2e", paper_bgcolor="#0e1117",
                               font_color="#ccd6f6", height=100, showlegend=True,
                               margin=dict(t=5, b=5), xaxis=dict(showticklabels=False),
                               legend=dict(orientation="h", bgcolor="#1c1f2e"))
    st.plotly_chart(fig_ratings, use_container_width=True)
st.markdown("---")
# ── News Sentiment ─────────────────────────────────────────────────────────────
st.markdown("### 📰 News Sentiment Analysis")
ns = d.get('news_sentiment')

if ns:
    sentiment_color = "#00b386" if "BULL" in ns['sentiment'] else "#ff6b6b" if "BEAR" in ns['sentiment'] else "#ffd700"
    score = ns['score']
    score_color = "#00b386" if score > 2 else "#ff6b6b" if score < -2 else "#ffd700"

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Sentiment", ns['sentiment'])
    col2.metric("Sentiment Score", f"{score:+.1f} / 10")
    col3.metric("Headlines Analyzed", ns['num_headlines'])

    st.markdown("**AI Analysis:**")
    st.markdown(ns['full_analysis'])

    with st.expander("View Headlines"):
        for h in ns['headlines']:
            st.markdown(f"- {h}")
else:
    st.caption("No news data available for this ticker.")
st.markdown("---")


# ── 6. FCF projection table ────────────────────────────────────────────────────
st.markdown("### FCF Projection Model")
st.caption("Revenue → EBIT → NOPAT + D&A − CapEx − ΔNWC = Unlevered FCF")
display_cols = ["Year", "Revenue ($B)", "Gross Profit ($B)", "EBIT ($B)",
                "NOPAT ($B)", "D&A ($B)", "CapEx ($B)", "ΔNWC ($B)", "FCF ($B)"]
st.dataframe(d['proj_df'][display_cols].set_index("Year"), use_container_width=True)


m = d['hist_metrics']
col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Margin (hist avg)", f"{m['gross_margin']*100:.1f}%")
col2.metric("EBIT Margin (hist avg)", f"{m['ebit_margin']*100:.1f}%")
col3.metric("CapEx % Revenue", f"{m['capex_pct']*100:.1f}%")
col4.metric("D&A % Revenue", f"{m['da_pct']*100:.1f}%")
st.markdown("---")


# ── 7. Monte Carlo ─────────────────────────────────────────────────────────────
st.markdown("### Monte Carlo Simulation")
st.caption("1,000 simulations randomizing WACC, growth rate, and terminal growth")
col1, col2 = st.columns([2, 1])
with col1:
    fig_mc = go.Figure()
    fig_mc.add_trace(go.Histogram(x=d['mc_results'], nbinsx=50, marker_color="#4a9eff", opacity=0.75))
    fig_mc.add_vline(x=d['current_price'], line_color="#ff6b6b", line_width=2, annotation_text="Current Price")
    fig_mc.add_vline(x=d['mc_results'].median(), line_color="#64ffda", line_width=2, annotation_text="Median")
    fig_mc.update_layout(plot_bgcolor="#1c1f2e", paper_bgcolor="#0e1117", font_color="#ccd6f6",
                         title="Distribution of Intrinsic Value Estimates",
                         xaxis_title="Value Per Share ($)", yaxis_title="Frequency")
    st.plotly_chart(fig_mc, use_container_width=True)
with col2:
    st.markdown("**Percentile Breakdown**")
    for label, q in [("5th (Bear)", 0.05), ("25th", 0.25), ("50th (Base)", 0.50), ("75th", 0.75), ("95th (Bull)", 0.95)]:
        st.metric(label, f"${d['mc_results'].quantile(q):,.2f}")
    st.markdown("---")
    st.metric("Probability Overvalued", f"{(d['mc_results'] < d['current_price']).mean()*100:.1f}%")
st.markdown("---")


# ── 8. Comps ───────────────────────────────────────────────────────────────────
st.markdown("### Comparable Companies Analysis")
st.dataframe(d['comps_df'].set_index("Ticker"), use_container_width=True)
st.markdown("#### Implied Share Price from Peer Multiples")
col1, col2, col3 = st.columns(3)
col1.metric("EV/EBITDA Implied", f"${d['implied_ev_ebitda']:,.2f}" if d['implied_ev_ebitda'] else "N/A", f"Avg: {d['avg_ev_ebitda']:.1f}x")
col2.metric("P/E Implied", f"${d['implied_pe']:,.2f}" if d['implied_pe'] else "N/A", f"Avg: {d['avg_pe']:.1f}x")
col3.metric("P/FCF Implied", f"${d['implied_p_fcf']:,.2f}" if d['implied_p_fcf'] else "N/A", f"Avg: {d['avg_p_fcf']:.1f}x")
st.markdown("---")


# ── 9. Sensitivity analysis ────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### DCF Assumptions")
    st.markdown(f"**Year 1 FCF Growth:** {d['growth_rate']*100:.1f}%")
    st.markdown(f"**Terminal Growth:** {d['terminal_growth']*100:.1f}%")
    st.markdown(f"**Exit Multiple:** {d['exit_multiple']}x EV/EBITDA")
    st.markdown(f"**WACC:** {d['wacc']*100:.2f}%")
    st.markdown(f"**Beta:** {d['info'].get('beta','N/A')}")
    st.markdown(f"**Market Cap:** ${d['info'].get('marketCap',0)/1e9:,.1f}B")
with col2:
    st.markdown("### Sensitivity Analysis")
    st.caption("Enterprise Value in $B across WACC and Terminal Growth Rate assumptions")
    sensitivity_df = sensitivity_analysis(d['fcf'], d['wacc'], d['growth_rate'], d['terminal_growth'])
    st.dataframe(sensitivity_df.style.background_gradient(cmap="RdYlGn"), use_container_width=True)
st.markdown("---")


# ── 10. Football field ─────────────────────────────────────────────────────────
st.markdown("### Football Field Chart")
ff_fig = build_football_field(
    d['current_price'], d['iv_midpoint'], d['mc_results'],
    d['implied_ev_ebitda'], d['implied_pe'], d['implied_p_fcf']
)
st.plotly_chart(ff_fig, use_container_width=True)
st.markdown("---")


# ── 11. Insider trading ────────────────────────────────────────────────────────
st.markdown("### Insider Trading")
if d['insider_summary']:
    ins = d['insider_summary']
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Buys", f"{ins['total_buys']:,}")
    col2.metric("Total Sells", f"{ins['total_sells']:,}")
    col3.metric("Net Shares", f"{ins['net_shares']:,}")
    col4.metric("Sentiment", ins['sentiment'])
if d['insider_df'] is not None:
    st.dataframe(d['insider_df'], use_container_width=True)
else:
    st.caption("No insider trading data available.")
st.markdown("---")


# ── 12. Earnings estimates ─────────────────────────────────────────────────────
st.markdown("### Earnings Estimates")
if d['earnings_data']:
    tab1, tab2, tab3 = st.tabs(["EPS Estimates", "Revenue Estimates", "EPS History"])
    with tab1:
        if d['earnings_data']["earnings_estimate"] is not None:
            st.dataframe(d['earnings_data']["earnings_estimate"], use_container_width=True)
    with tab2:
        if d['earnings_data']["revenue_estimate"] is not None:
            st.dataframe(d['earnings_data']["revenue_estimate"], use_container_width=True)
    with tab3:
        if d['earnings_data']["earnings_history"] is not None:
            st.dataframe(d['earnings_data']["earnings_history"], use_container_width=True)
else:
    st.caption("No earnings data available.")
st.markdown("---")


# ── 13. DDM ────────────────────────────────────────────────────────────────────
st.markdown("### Dividend Discount Model (DDM)")
ddm = d.get('ddm_data', {'applicable': False, 'reason': 'No data'})
if not ddm['applicable']:
    st.caption(f"DDM not applicable: {ddm['reason']}")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DDM Intrinsic Value", f"${ddm['ddm_value']:,.2f}")
    col2.metric("Current Price", f"${ddm['current_price']:,.2f}")
    col3.metric("Upside/Downside", f"{ddm['upside']:,.1f}%", delta=f"{ddm['upside']:,.1f}%")
    col4.metric("Dividend Yield", f"{ddm['dividend_yield']*100:.2f}%" if ddm['dividend_yield'] else "N/A")
    col1, col2, col3 = st.columns(3)
    col1.metric("Annual Dividend", f"${ddm['dividend_rate']:,.2f}")
    col2.metric("Dividend Growth Rate", f"{ddm['dividend_growth']*100:.1f}%")
    col3.metric("Payout Ratio", f"{ddm['payout_ratio']*100:.1f}%" if ddm['payout_ratio'] else "N/A")
    st.caption("Gordon Growth Model: P = D1 / (WACC − g)")
st.markdown("---")


# ── 14. Financial statements ───────────────────────────────────────────────────
with st.expander("View Full Financial Statements"):
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Cash Flow", "Balance Sheet"])
    with tab1:
        st.dataframe(d['income_stmt'], use_container_width=True)
    with tab2:
        st.dataframe(d['cash_flow'], use_container_width=True)
    with tab3:
        st.dataframe(d['balance_sheet'], use_container_width=True)
st.markdown("---")
# ── Portfolio Screener ─────────────────────────────────────────────────────────
st.markdown("### 🔍 Portfolio Screener")
st.caption("Screen multiple stocks simultaneously and rank by undervaluation")

default_tickers = "AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, JPM, V, JNJ"
ticker_input = st.text_area("Enter tickers separated by commas", value=default_tickers, height=68)

if st.button("Run Screener", use_container_width=True):
    tickers_list = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    with st.spinner(f"Screening {len(tickers_list)} stocks — this may take a minute..."):
        screener_df = screen_tickers(
            tickers_list,
            d['growth_rate'],
            d['terminal_growth'],
            d['exit_multiple']
        )
        st.session_state.screener_df = screener_df

if "screener_df" in st.session_state:
    df = st.session_state.screener_df
    st.dataframe(
        df.style.background_gradient(subset=["Upside/Downside (%)"], cmap="RdYlGn"),
        use_container_width=True
    )
    st.download_button(
        "⬇️ Download Screener Results",
        df.to_csv(index=False),
        file_name="screener_results.csv",
        mime="text/csv",
        use_container_width=True
    )
st.markdown("---")

# ── 15. Export ─────────────────────────────────────────────────────────────────
st.markdown("### Export Reports")
col1, col2 = st.columns(2)
with col1:
    st.download_button("Download PDF Report", d['pdf_bytes'],
                       file_name=d['pdf_filename'], mime="application/pdf", use_container_width=True)
with col2:
    st.download_button("Download Excel Model", d['excel_bytes'],
                       file_name=d['excel_filename'],
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

# ── AI Equity Research Report ──────────────────────────────────────────────────
st.markdown("### 🤖 AI Equity Research Report")
st.caption("Powered by LLaMA 3.3 70B — generates a full sell-side style report from your data")


if st.button("Generate AI Report", use_container_width=True):
    with st.spinner("Writing equity research report..."):
        ai_report = generate_ai_report(
            d['ticker'], d['company_name'], d['current_price'],
            d['iv_midpoint'], d['iv_perpetuity'], d['iv_multiple'],
            d['wacc'], d['growth_rate'], d['terminal_growth'],
            d['ratios'], d['comps_df'], d['analyst_data'],
            d['hist_metrics'], d['proj_df'], d['mc_results'],
            d['insider_summary'], d['info']
        )
        st.session_state.ai_report = ai_report


if "ai_report" in st.session_state:
    st.markdown(st.session_state.ai_report)
    st.download_button(
        "⬇️ Download Report as Text",
        st.session_state.ai_report,
        file_name=f"{d['ticker']}_equity_research_report.txt",
        mime="text/plain",
        use_container_width=True
    )
st.markdown("---")




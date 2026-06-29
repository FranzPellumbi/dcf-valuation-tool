import plotly.graph_objects as go

def build_football_field(current_price, intrinsic_value, mc_results, 
                          implied_ev_ebitda, implied_pe, implied_p_fcf):
    methods = []
    lows = []
    highs = []

    # DCF range
    methods.append("DCF")
    lows.append(intrinsic_value * 0.85)
    highs.append(intrinsic_value * 1.15)

    # Monte Carlo range
    methods.append("Monte Carlo")
    lows.append(mc_results.quantile(0.25))
    highs.append(mc_results.quantile(0.75))

    # EV/EBITDA range
    if implied_ev_ebitda:
        methods.append("EV/EBITDA Comps")
        lows.append(implied_ev_ebitda * 0.85)
        highs.append(implied_ev_ebitda * 1.15)

    # P/E range
    if implied_pe:
        methods.append("P/E Comps")
        lows.append(implied_pe * 0.85)
        highs.append(implied_pe * 1.15)

    # P/FCF range
    if implied_p_fcf:
        methods.append("P/FCF Comps")
        lows.append(implied_p_fcf * 0.85)
        highs.append(implied_p_fcf * 1.15)

    # Build chart — invisible base bar + visible range bar
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=methods,
        x=lows,
        orientation="h",
        marker=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Bar(
        y=methods,
        x=[h - l for h, l in zip(highs, lows)],
        orientation="h",
        marker=dict(color="#4a9eff", opacity=0.7),
        name="Valuation Range",
        hovertemplate="Low: $%{base:,.2f}<br>High: $%{x:,.2f}<extra></extra>",
        base=lows
    ))

    # Current price line
    fig.add_vline(
        x=current_price,
        line_color="#ff6b6b",
        line_width=2,
        annotation_text=f"Current: ${current_price:,.2f}",
        annotation_font_color="#ff6b6b"
    )

    fig.update_layout(
        barmode="stack",
        plot_bgcolor="#1c1f2e",
        paper_bgcolor="#0e1117",
        font_color="#ccd6f6",
        title="Football Field — Valuation Range by Method",
        xaxis_title="Share Price ($)",
        height=350,
        showlegend=False,
        xaxis=dict(gridcolor="#2d3250")
    )

    return fig


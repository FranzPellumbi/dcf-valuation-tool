from dcf import calculate_dcf_full, project_fcf_detailed

def run_scenarios(hist_metrics, wacc, terminal_growth, exit_multiple, shares_outstanding):
    
    # ── Bear Case ──────────────────────────────────────────────────────────────
    bear_metrics = hist_metrics.copy()
    bear_metrics["ebit_margin"] = hist_metrics["ebit_margin"] * 0.85
    bear_metrics["gross_margin"] = hist_metrics["gross_margin"] * 0.92
    bear_growth = max(hist_metrics.get("revenue_growth", 0.03), 0.02)
    bear_wacc = wacc + 0.015
    bear_terminal = max(terminal_growth - 0.005, 0.01)

    bear_proj, bear_fcf_list, bear_ebitda = project_fcf_detailed(
        bear_metrics, bear_growth, bear_terminal
    )
    bear_dcf = calculate_dcf_full(bear_fcf_list, bear_ebitda, bear_wacc, bear_terminal, exit_multiple - 2)
    bear_iv = bear_dcf["total_pv_midpoint"] / shares_outstanding

    # ── Base Case ──────────────────────────────────────────────────────────────
    base_proj, base_fcf_list, base_ebitda = project_fcf_detailed(
        hist_metrics, hist_metrics.get("revenue_growth", 0.06), terminal_growth
    )
    base_dcf = calculate_dcf_full(base_fcf_list, base_ebitda, wacc, terminal_growth, exit_multiple)
    base_iv = base_dcf["total_pv_midpoint"] / shares_outstanding

    # ── Bull Case ──────────────────────────────────────────────────────────────
    bull_metrics = hist_metrics.copy()
    bull_metrics["ebit_margin"] = hist_metrics["ebit_margin"] * 1.15
    bull_metrics["gross_margin"] = hist_metrics["gross_margin"] * 1.05
    bull_growth = hist_metrics.get("revenue_growth", 0.08) * 1.3
    bull_wacc = wacc - 0.01
    bull_terminal = terminal_growth + 0.005

    bull_proj, bull_fcf_list, bull_ebitda = project_fcf_detailed(
        bull_metrics, bull_growth, bull_terminal
    )
    bull_dcf = calculate_dcf_full(bull_fcf_list, bull_ebitda, bull_wacc, bull_terminal, exit_multiple + 2)
    bull_iv = bull_dcf["total_pv_midpoint"] / shares_outstanding

    return {
        "bear": {
            "iv": round(bear_iv, 2),
            "wacc": round(bear_wacc * 100, 2),
            "growth": round(bear_growth * 100, 2),
            "terminal": round(bear_terminal * 100, 2),
            "exit_multiple": exit_multiple - 2,
            "ebit_margin": round(bear_metrics["ebit_margin"] * 100, 2),
            "label": "Bear Case",
            "color": "#ff6b6b"
        },
        "base": {
            "iv": round(base_iv, 2),
            "wacc": round(wacc * 100, 2),
            "growth": round(hist_metrics.get("revenue_growth", 0.06) * 100, 2),
            "terminal": round(terminal_growth * 100, 2),
            "exit_multiple": exit_multiple,
            "ebit_margin": round(hist_metrics["ebit_margin"] * 100, 2),
            "label": "Base Case",
            "color": "#4a9eff"
        },
        "bull": {
            "iv": round(bull_iv, 2),
            "wacc": round(bull_wacc * 100, 2),
            "growth": round(bull_growth * 100, 2),
            "terminal": round(bull_terminal * 100, 2),
            "exit_multiple": exit_multiple + 2,
            "ebit_margin": round(bull_metrics["ebit_margin"] * 100, 2),
            "label": "Bull Case",
            "color": "#00b386"
        }
    }


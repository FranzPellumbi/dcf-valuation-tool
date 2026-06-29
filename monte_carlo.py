import numpy as np
import pandas as pd
from dcf import calculate_dcf

def run_monte_carlo(fcf, wacc, growth_rate, terminal_growth, shares_outstanding, simulations=1000):
    results = []

    for _ in range(simulations):
        # Randomize inputs around base assumptions
        sim_wacc = np.random.normal(wacc, 0.01)
        sim_growth = np.random.normal(growth_rate, 0.02)
        sim_terminal = np.random.normal(terminal_growth, 0.005)

        # Skip invalid combos
        if sim_wacc <= sim_terminal or sim_wacc <= 0 or sim_growth <= 0:
            continue

        total_pv, _, _, _ = calculate_dcf(fcf, sim_wacc, sim_growth, sim_terminal)
        intrinsic_value = total_pv / shares_outstanding
        results.append(intrinsic_value)

    return pd.Series(results)


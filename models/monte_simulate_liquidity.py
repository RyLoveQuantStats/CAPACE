#!/usr/bin/env python3
"""
simulate_liquidity_monte_carlo.py

Runs Monte Carlo simulations on the 'capital_calls' time series from the merged data,
estimates daily changes, and computes potential future outcomes.

Enhancements:
 - Clips simulated outcomes to a floor of zero (since negative capital calls are unrealistic).
 - Prints simulation percentiles.
"""

import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "database/blackstone_data.db"
TABLE_NAME = "bx_master_data"

def load_master_data(db_path=DB_PATH, table=TABLE_NAME):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table}", conn, parse_dates=["Date"])
    conn.close()
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    return df

def main():
    df = load_master_data()
    if "capital_calls" not in df.columns:
        raise ValueError("❌ 'capital_calls' column not found. Check your data ingestion pipeline.")
    
    df["calls_change"] = df["capital_calls"].diff().fillna(0)
    mean_change = df["calls_change"].mean()
    std_change = df["calls_change"].std()
    print(f"Mean daily change: {mean_change:.2f}, Std: {std_change:.2f}")
    
    n_simulations = 100000
    horizon = 30  # Forecast horizon (e.g., 30 days)
    last_value = df["capital_calls"].iloc[-1]
    
    outcomes = []
    for _ in range(n_simulations):
        shocks = np.random.normal(mean_change, std_change, horizon)
        simulated_value = last_value + np.sum(shocks)
        # Capital calls cannot be negative: clip to 0
        outcomes.append(max(0, simulated_value))
    
    outcomes = np.array(outcomes)
    p5 = np.percentile(outcomes, 5)
    p50 = np.percentile(outcomes, 50)
    p95 = np.percentile(outcomes, 95)
    
    print(f"5th percentile: {p5:.2f}")
    print(f"Median: {p50:.2f}")
    print(f"95th percentile: {p95:.2f}")

if __name__ == "__main__":
    main()

import pandas as pd


def compute_metrics(results_df: pd.DataFrame) -> dict:
    """
    results_df expected columns:
    - demand
    - fulfilled

    Returns:
    - stockout_pct
    - fill_rate
    - total_demand
    - total_fulfilled
    """

    total_demand = results_df["demand"].sum()
    total_fulfilled = results_df["fulfilled"].sum()

    if total_demand == 0:
        return {
            "stockout_pct": 0,
            "fill_rate": 1,
            "total_demand": 0,
            "total_fulfilled": 0,
        }

    stockout_pct = 1 - (total_fulfilled / total_demand)
    fill_rate = total_fulfilled / total_demand

    return {
        "stockout_pct": float(round(stockout_pct, 3)),
        "fill_rate": float(round(fill_rate, 3)),
        "total_demand": int(total_demand),
        "total_fulfilled": int(total_fulfilled),
    }
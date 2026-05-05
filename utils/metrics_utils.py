import pandas as pd


def compute_metrics(results_df: pd.DataFrame) -> dict:

    total_demand = results_df["demand"].sum()
    total_fulfilled = results_df["fulfilled"].sum()

    if total_demand == 0:
        return {
            "stockout_pct": 0,
            "fill_rate": 1,
            "total_demand": 0,
            "total_fulfilled": 0,
            "efficiency_score": 100
        }

    fill_rate = total_fulfilled / total_demand
    stockout_pct = 1 - fill_rate

    # -----------------------------
    # NEW → Efficiency Score
    # -----------------------------
    # Simple weighted score (MVP)
    efficiency_score = (
        fill_rate * 100
        - stockout_pct * 50
    )

    return {
        "stockout_pct": float(round(stockout_pct, 3)),
        "fill_rate": float(round(fill_rate, 3)),
        "total_demand": int(total_demand),
        "total_fulfilled": int(total_fulfilled),
        "efficiency_score": float(round(efficiency_score, 2))
    }
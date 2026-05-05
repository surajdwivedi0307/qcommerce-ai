import pandas as pd


def compute_priority(inventory_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple priority score:
    Lower stock → higher priority

    Returns:
    DataFrame with:
    - store_id
    - sku_id
    - stock
    - priority_score
    """

    df = inventory_df.copy()

    # Simple inverse scoring (lower stock = higher priority)
    df["priority_score"] = 1 / (df["stock"] + 1)

    # Sort highest priority first
    df = df.sort_values(by="priority_score", ascending=False)

    return df
import pandas as pd


def generate_replenishment_plan(inventory_df: pd.DataFrame,
                                target_stock: int = 50) -> pd.DataFrame:
    """
    Simple replenishment logic:
    If stock < target → replenish up to target

    Returns:
    DataFrame with:
    - store_id
    - sku_id
    - replenish_qty
    """

    records = []

    for _, row in inventory_df.iterrows():
        current_stock = row["stock"]

        if current_stock < target_stock:
            replenish_qty = target_stock - current_stock

            records.append({
                "store_id": row["store_id"],
                "sku_id": row["sku_id"],
                "replenish_qty": replenish_qty
            })

    return pd.DataFrame(records)
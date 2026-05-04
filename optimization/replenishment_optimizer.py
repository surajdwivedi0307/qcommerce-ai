import pandas as pd
from configs.settings import settings


def generate_replenishment_plan(inventory_df: pd.DataFrame,
                                target_stock: int = settings.TARGET_STOCK) -> pd.DataFrame:

    records = []

    for _, row in inventory_df.iterrows():
        current_stock = row["stock"]

        if current_stock < target_stock:

            needed = target_stock - current_stock

            # Cost logic
            holding_cost = needed * settings.HOLDING_COST_PER_UNIT
            stockout_risk_cost = needed * settings.STOCKOUT_PENALTY_PER_UNIT

            # Decision
            if stockout_risk_cost > holding_cost:
                replenish_qty = needed
            else:
                replenish_qty = 0

            if replenish_qty > 0:
                records.append({
                    "store_id": row["store_id"],
                    "sku_id": row["sku_id"],
                    "replenish_qty": replenish_qty
                })

    return pd.DataFrame(records)
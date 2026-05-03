import numpy as np
import pandas as pd


def initialize_inventory(stores_df, sku_df, coverage_days=2):
    """
    Initialize starting inventory based on base demand * coverage days
    """
    records = []

    for _, store in stores_df.iterrows():
        for _, sku in sku_df.iterrows():
            initial_stock = int(sku["base_demand"] * coverage_days * np.random.uniform(0.8, 1.2))

            records.append({
                "store_id": store["store_id"],
                "sku_id": sku["sku_id"],
                "stock": initial_stock
            })

    return pd.DataFrame(records)


def simulate_inventory(demand_df, inventory_df):
    """
    Simulate inventory consumption and track stockouts
    """
    inventory = inventory_df.copy()
    inventory.set_index(["store_id", "sku_id"], inplace=True)

    results = []

    for _, row in demand_df.iterrows():
        key = (row["store_id"], row["sku_id"])

        if key not in inventory.index:
            continue

        available_stock = inventory.loc[key, "stock"]
        demand = row["demand"]

        fulfilled = min(available_stock, demand)
        lost_sales = max(0, demand - available_stock)

        # update stock
        inventory.loc[key, "stock"] -= fulfilled

        results.append({
            "store_id": row["store_id"],
            "sku_id": row["sku_id"],
            "day": row["day"],
            "hour": row["hour"],
            "demand": demand,
            "fulfilled": fulfilled,
            "lost_sales": lost_sales,
            "ending_stock": inventory.loc[key, "stock"]
        })

    return pd.DataFrame(results), inventory.reset_index()


def generate_replenishment_signals(inventory_df, threshold=20):
    """
    Flag low stock items for replenishment
    """
    signals = inventory_df[inventory_df["stock"] < threshold].copy()

    signals["replenishment_qty"] = (threshold * 2) - signals["stock"]

    return signals
import numpy as np
import pandas as pd


def initialize_inventory(stores_df, sku_df, coverage_days=2):
    """
    Initialize starting inventory with strong store + SKU variation
    """
    import numpy as np
    import pandas as pd

    records = []

    # SKU-level bias: some SKUs are naturally overstocked (creates surplus)
    sku_bias_map = {
        sku["sku_id"]: np.random.uniform(0.8, 1.8)  # up to 1.8x for some SKUs
        for _, sku in sku_df.iterrows()
    }

    for _, store in stores_df.iterrows():
        # stronger store-level bias
        store_bias = np.random.uniform(0.5, 1.8)

        for _, sku in sku_df.iterrows():
            sku_bias = sku_bias_map[sku["sku_id"]]

            initial_stock = int(
                sku["base_demand"] *
                coverage_days *
                store_bias *
                sku_bias *
                np.random.uniform(0.8, 1.2)
            )

            records.append({
                "store_id": store["store_id"],
                "sku_id": sku["sku_id"],
                "stock": max(0, initial_stock)
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

        

        # Cap fulfillment per step (IMPORTANT FIX)
        max_fulfillment = int(available_stock * 0.3)  # only 30% consumed per hour
        fulfilled = min(max_fulfillment, demand)
        lost_sales = max(0, demand - fulfilled)
        

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

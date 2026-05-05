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
    Simulates fulfillment based on demand and available stock
    """

    inventory = inventory_df.copy()
    results = []

    for _, row in demand_df.iterrows():

        store = row["store_id"]
        sku = row["sku_id"]
        demand = row["demand"]

        # Get current stock (SAFE extraction)
        stock_row = inventory.loc[
            (inventory["store_id"] == store) &
            (inventory["sku_id"] == sku),
            "stock"
        ]

        if len(stock_row) == 0:
            available_stock = 0
        else:
            available_stock = stock_row.iloc[0]

        # Fulfillment logic
        max_fulfillment = int(available_stock * 0.3)
        fulfilled = min(demand, max_fulfillment)

        # Update inventory
        inventory.loc[
            (inventory["store_id"] == store) &
            (inventory["sku_id"] == sku),
            "stock"
        ] -= fulfilled

        results.append({
            "store_id": store,
            "sku_id": sku,
            "demand": demand,
            "fulfilled": fulfilled
        })

    results_df = pd.DataFrame(results)

    return results_df, inventory


def generate_replenishment_signals(inventory_df, threshold=20):
    """
    Flag low stock items for replenishment
    """
    signals = inventory_df[inventory_df["stock"] < threshold].copy()

    signals["replenishment_qty"] = (threshold * 2) - signals["stock"]

    return signals

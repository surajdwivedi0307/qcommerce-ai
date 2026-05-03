import numpy as np
import pandas as pd

np.random.seed(42)


def generate_sku_master(num_skus=100):
    """
    Create SKU catalog with categories
    """
    categories = ["Fruits", "Dairy", "Snacks", "Beverages", "Staples"]

    skus = []
    for i in range(num_skus):
        skus.append({
            "sku_id": f"SKU{i+1}",
            "category": np.random.choice(categories),
            "base_demand": np.random.randint(5, 50),
        })

    return pd.DataFrame(skus)


def generate_hourly_demand(stores_df, sku_df, days=7):
    """
    Generate demand time series
    """
    records = []

    for _, store in stores_df.iterrows():

        # store-level variation
        store_multiplier = np.random.uniform(0.8, 1.2)

        for _, sku in sku_df.iterrows():
            for day in range(days):
                for hour in range(24):

                    # Base demand with store variation
                    # Convert daily demand → hourly demand
                    demand = (sku["base_demand"] / 24) * store_multiplier

                    # Weekend effect (milder)
                    if day % 7 in [5, 6]:
                        demand *= 1.1

                    # Peak hours (milder)
                    if 8 <= hour <= 11 or 18 <= hour <= 22:
                        demand *= 1.2

                    # Random noise
                    demand *= np.random.uniform(0.9, 1.1)

                    records.append({
                        "store_id": store["store_id"],
                        "sku_id": sku["sku_id"],
                        "day": day,
                        "hour": hour,
                        "demand": int(demand),
                    })

    return pd.DataFrame(records)
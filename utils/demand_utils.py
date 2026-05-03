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
        for _, sku in sku_df.iterrows():
            for day in range(days):
                for hour in range(24):

                    # Base demand
                    demand = sku["base_demand"]

                    # Weekend effect
                    if day % 7 in [5, 6]:
                        demand *= 1.2

                    # Peak hours (morning + evening)
                    if 8 <= hour <= 11 or 18 <= hour <= 22:
                        demand *= 1.5

                    # Random noise
                    demand *= np.random.uniform(0.7, 1.3)

                    records.append({
                        "store_id": store["store_id"],
                        "sku_id": sku["sku_id"],
                        "day": day,
                        "hour": hour,
                        "demand": int(demand),
                    })

    return pd.DataFrame(records)
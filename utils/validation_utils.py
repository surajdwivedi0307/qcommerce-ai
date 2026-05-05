import pandas as pd


def validate_demand(demand_df: pd.DataFrame):
    required_cols = {"store_id", "sku_id", "demand"}

    if not required_cols.issubset(demand_df.columns):
        return False, f"Demand CSV must contain columns: {required_cols}"

    if demand_df["demand"].isnull().any():
        return False, "Demand column contains missing values"

    if (demand_df["demand"] < 0).any():
        return False, "Demand cannot be negative"

    return True, "Demand data valid"


def validate_inventory(inventory_df: pd.DataFrame):
    required_cols = {"store_id", "sku_id", "stock"}

    if not required_cols.issubset(inventory_df.columns):
        return False, f"Inventory CSV must contain columns: {required_cols}"

    if inventory_df["stock"].isnull().any():
        return False, "Stock column contains missing values"

    if (inventory_df["stock"] < 0).any():
        return False, "Stock cannot be negative"

    return True, "Inventory data valid"
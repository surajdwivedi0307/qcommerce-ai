import pandas as pd


def identify_surplus_deficit(ending_inventory, threshold=20):
    """
    Identify surplus and deficit stores per SKU
    """
    surplus = ending_inventory[ending_inventory["stock"] > threshold].copy()
    deficit = ending_inventory[ending_inventory["stock"] < threshold].copy()

    surplus["surplus_qty"] = surplus["stock"] - threshold
    deficit["deficit_qty"] = threshold - deficit["stock"]

    return surplus, deficit


def generate_transfer_plan(surplus_df, deficit_df, distance_matrix, transfer_mask):
    """
    Generate transfer plan based on:
    - surplus availability
    - deficit need
    - distance constraint
    """

    transfers = []

    for _, d_row in deficit_df.iterrows():
        d_store = d_row["store_id"]
        sku = d_row["sku_id"]
        deficit_qty = d_row["deficit_qty"]

        # find eligible surplus stores
        eligible_sources = []

        for _, s_row in surplus_df.iterrows():
            if s_row["sku_id"] != sku:
                continue

            s_store = s_row["store_id"]

            if transfer_mask.loc[s_store, d_store]:
                distance = distance_matrix.loc[s_store, d_store]

                eligible_sources.append({
                    "source": s_store,
                    "distance": distance,
                    "available": s_row["surplus_qty"]
                })

        # sort by closest first
        eligible_sources = sorted(eligible_sources, key=lambda x: x["distance"])

        remaining = deficit_qty

        for source in eligible_sources:
            if remaining <= 0:
                break

            transfer_qty = min(source["available"], remaining)

            transfers.append({
                "sku_id": sku,
                "from_store": source["source"],
                "to_store": d_store,
                "quantity": transfer_qty,
                "distance_km": source["distance"]
            })

            remaining -= transfer_qty

    return pd.DataFrame(transfers)
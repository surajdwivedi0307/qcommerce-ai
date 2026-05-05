import pandas as pd

from utils.inventory_utils import simulate_inventory
from optimization.transfer_optimizer import identify_surplus_deficit, generate_transfer_plan
from optimization.replenishment_optimizer import generate_replenishment_plan
from optimization.priority_engine import compute_priority
from utils.metrics_utils import compute_metrics
from utils.geo_utils import generate_stores, compute_distance_matrix, compute_transfer_mask
from configs.settings import settings


def apply_transfers(inventory, transfers):
    if len(transfers) == 0:
        return inventory

    inventory = inventory.copy()

    for _, row in transfers.iterrows():
        sku = row["sku_id"]
        from_store = row["from_store"]
        to_store = row["to_store"]
        qty = row["quantity"]

        inventory.loc[
            (inventory["store_id"] == from_store) &
            (inventory["sku_id"] == sku),
            "stock"
        ] -= qty

        inventory.loc[
            (inventory["store_id"] == to_store) &
            (inventory["sku_id"] == sku),
            "stock"
        ] += qty

    return inventory


def apply_replenishment(inventory, replenishment):
    if len(replenishment) == 0:
        return inventory

    inventory = inventory.copy()

    for _, row in replenishment.iterrows():
        inventory.loc[
            (inventory["store_id"] == row["store_id"]) &
            (inventory["sku_id"] == row["sku_id"]),
            "stock"
        ] += row["replenish_qty"]

    return inventory


def run_with_data(demand_df: pd.DataFrame, inventory_df: pd.DataFrame, num_days=3):

    stores = demand_df["store_id"].unique()
    dist = compute_distance_matrix(generate_stores(len(stores)))
    mask = compute_transfer_mask(dist, settings.MAX_DISTANCE_KM)

    inventory = inventory_df.copy()
    all_logs = []

    for day in range(num_days):

        # Filter one day if timestamp exists
        demand = demand_df.copy()

        results, ending_inventory = simulate_inventory(demand, inventory)

        priority_df = compute_priority(ending_inventory)
        replenishment = generate_replenishment_plan(ending_inventory)
        metrics = compute_metrics(results)

        surplus, deficit = identify_surplus_deficit(
            ending_inventory,
            threshold=settings.SURPLUS_THRESHOLD
        )

        transfers = generate_transfer_plan(surplus, deficit, dist, mask)

        inventory = apply_transfers(ending_inventory, transfers)
        inventory = apply_replenishment(inventory, replenishment)

        top_priority = priority_df.head(3)[["store_id", "sku_id", "stock"]]

        all_logs.append({
            "day": day + 1,
            "transfers": transfers,
            "metrics": metrics,
            "top_priority": top_priority
        })

    return all_logs
from utils.geo_utils import generate_stores
from utils.demand_utils import generate_sku_master, generate_hourly_demand
from utils.inventory_utils import initialize_inventory, simulate_inventory
from optimization.transfer_optimizer import identify_surplus_deficit, generate_transfer_plan
from utils.logger import logger
from configs.settings import settings
from utils.geo_utils import compute_distance_matrix, compute_transfer_maskls pipelines

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


def run_simulation():
    logger.info("Starting multi-day simulation")

    stores = generate_stores(5)
    skus = generate_sku_master(10)

    inventory = initialize_inventory(
        stores,
        skus,
        coverage_days=settings.INVENTORY_COVERAGE_DAYS
    )

    all_logs = []

    for day in range(settings.SIMULATION_DAYS):
        logger.info(f"Day {day+1} started")

        demand = generate_hourly_demand(stores, skus, days=1)
        _, ending_inventory = simulate_inventory(demand, inventory)

        surplus, deficit = identify_surplus_deficit(
            ending_inventory,
            threshold=settings.SURPLUS_THRESHOLD
        )

        dist = compute_distance_matrix(stores)
        mask = compute_transfer_mask(dist, settings.MAX_DISTANCE_KM)

        transfers = generate_transfer_plan(surplus, deficit, dist, mask)

        inventory = apply_transfers(ending_inventory, transfers)

        all_logs.append({
            "day": day + 1,
            "transfers": transfers
        })

    logger.info("Simulation complete")

    return all_logs
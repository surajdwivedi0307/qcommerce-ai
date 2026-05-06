from utils.geo_utils import (
    generate_stores,
    compute_distance_matrix,
    compute_transfer_mask
)

from utils.demand_utils import (
    generate_sku_master,
    generate_hourly_demand
)

from utils.inventory_utils import (
    initialize_inventory,
    simulate_inventory
)

from optimization.transfer_optimizer import (
    identify_surplus_deficit,
    generate_transfer_plan
)

from optimization.replenishment_optimizer import (
    generate_replenishment_plan
)

from optimization.priority_engine import (
    compute_priority
)

from utils.metrics_utils import compute_metrics
from utils.logger import logger
from configs.settings import settings


# =====================================================
# APPLY TRANSFERS
# =====================================================
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


# =====================================================
# APPLY REPLENISHMENT
# =====================================================
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


# =====================================================
# MAIN SIMULATION
# =====================================================
def run_simulation(
    num_stores=5,
    num_skus=10,
    num_days=3
):

    logger.info("Starting multi-day simulation")

    # -----------------------------
    # Base Data
    # -----------------------------
    stores = generate_stores(num_stores)

    skus = generate_sku_master(num_skus)

    inventory = initialize_inventory(
        stores,
        skus,
        coverage_days=settings.INVENTORY_COVERAGE_DAYS
    )

    all_logs = []

    # =====================================================
    # DAY LOOP
    # =====================================================
    for day in range(num_days):

        logger.info(f"Day {day+1} started")

        # -----------------------------
        # Demand Simulation
        # -----------------------------
        demand = generate_hourly_demand(
            stores,
            skus,
            days=1
        )

        results, ending_inventory = simulate_inventory(
            demand,
            inventory
        )

        # -----------------------------
        # Priority Engine
        # -----------------------------
        priority_df = compute_priority(
            ending_inventory
        )

        # -----------------------------
        # Replenishment
        # -----------------------------
        replenishment = generate_replenishment_plan(
            ending_inventory
        )

        # -----------------------------
        # Metrics
        # -----------------------------
        metrics = compute_metrics(results)

        # -----------------------------
        # Surplus / Deficit
        # -----------------------------
        surplus, deficit = identify_surplus_deficit(
            ending_inventory,
            threshold=settings.SURPLUS_THRESHOLD
        )

        # -----------------------------
        # Distance Logic
        # -----------------------------
        dist = compute_distance_matrix(stores)

        mask = compute_transfer_mask(
            dist,
            settings.MAX_DISTANCE_KM
        )

        # -----------------------------
        # Transfer Optimization
        # -----------------------------
        transfers = generate_transfer_plan(
            surplus,
            deficit,
            dist,
            mask
        )

        # =====================================================
        # EXPLAINABILITY V2
        # =====================================================
        explain_dict = {}

        if len(transfers) > 0:

            for _, row in transfers.iterrows():

                sku = row["sku_id"]

                # -----------------------------
                # Create SKU Group
                # -----------------------------
                if sku not in explain_dict:

                    explain_dict[sku] = {
                        "sku_id": sku,
                        "events": []
                    }

                # -----------------------------
                # Source Stock
                # -----------------------------
                source_stock_before = ending_inventory.loc[
                    (ending_inventory["store_id"] == row["from_store"]) &
                    (ending_inventory["sku_id"] == sku),
                    "stock"
                ].iloc[0]

                # -----------------------------
                # Destination Stock
                # -----------------------------
                destination_stock_before = ending_inventory.loc[
                    (ending_inventory["store_id"] == row["to_store"]) &
                    (ending_inventory["sku_id"] == sku),
                    "stock"
                ].iloc[0]

                # -----------------------------
                # Cost Logic
                # -----------------------------
                transfer_cost = round(
                    row["quantity"] * row["distance_km"],
                    2
                )

                stockout_risk_cost = int(
                    row["quantity"] * 10
                )

                # -----------------------------
                # Future Context Placeholder
                # -----------------------------
                future_context = {
                    "inbound_inventory": 0,
                    "constraints": []
                }

                # -----------------------------
                # Decision Reason
                # -----------------------------
                decision_reason = (
                    "TRANSFER_THRESHOLD_BREACH"
                )

                # -----------------------------
                # Append Event
                # -----------------------------
                explain_dict[sku]["events"].append({

                    "event_type": "TRANSFER",

                    "from_store": row["from_store"],
                    "to_store": row["to_store"],

                    "source_stock_before": int(
                        source_stock_before
                    ),

                    "destination_stock_before": int(
                        destination_stock_before
                    ),

                    "threshold": int(
                        settings.SURPLUS_THRESHOLD
                    ),

                    "quantity": int(
                        row["quantity"]
                    ),

                    "distance_km": round(
                        float(row["distance_km"]),
                        2
                    ),

                    "cost": {

                        "transfer_cost": transfer_cost,

                        "stockout_risk_cost": stockout_risk_cost
                    },

                    "decision_reason": decision_reason,

                    "future_context": future_context
                })

        # -----------------------------
        # Dict → List
        # -----------------------------
        explain_list = list(
            explain_dict.values()
        )

        # -----------------------------
        # Apply Transfers
        # -----------------------------
        inventory = apply_transfers(
            ending_inventory,
            transfers
        )

        # -----------------------------
        # Apply Replenishment
        # -----------------------------
        inventory = apply_replenishment(
            inventory,
            replenishment
        )

        # -----------------------------
        # Top Priority
        # -----------------------------
        top_priority = priority_df.head(3)[
            ["store_id", "sku_id", "stock"]
        ]

        logger.info(
            f"Top priorities Day {day+1}:\n{top_priority}"
        )

        logger.info(
            f"Day {day+1} Metrics: {metrics}"
        )

        # -----------------------------
        # Final Day Log
        # -----------------------------
        all_logs.append({

            "day": day + 1,

            "transfers": transfers,

            "metrics": metrics,

            "top_priority": top_priority,

            "explain": explain_list,
            
            "stores": stores
        })

    logger.info("Simulation complete")

    return all_logs
import pandas as pd

from utils.inventory_utils import (
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

from utils.metrics_utils import (
    compute_metrics
)

from utils.geo_utils import (

    generate_stores,

    build_store_master,

    compute_distance_matrix,

    compute_transfer_mask
)

from configs.settings import settings


# =====================================================
# APPLY TRANSFERS
# =====================================================
def apply_transfers(
    inventory,
    transfers
):

    if len(transfers) == 0:
        return inventory

    inventory = inventory.copy()

    for _, row in transfers.iterrows():

        sku = row["sku_id"]

        from_store = row["from_store"]

        to_store = row["to_store"]

        qty = row["quantity"]

        inventory.loc[
            (
                inventory["store_id"]
                == from_store
            )
            &
            (
                inventory["sku_id"]
                == sku
            ),
            "stock"
        ] -= qty

        inventory.loc[
            (
                inventory["store_id"]
                == to_store
            )
            &
            (
                inventory["sku_id"]
                == sku
            ),
            "stock"
        ] += qty

    return inventory


# =====================================================
# APPLY REPLENISHMENT
# =====================================================
def apply_replenishment(
    inventory,
    replenishment
):

    if len(replenishment) == 0:
        return inventory

    inventory = inventory.copy()

    for _, row in replenishment.iterrows():

        inventory.loc[
            (
                inventory["store_id"]
                == row["store_id"]
            )
            &
            (
                inventory["sku_id"]
                == row["sku_id"]
            ),
            "stock"
        ] += row["replenish_qty"]

    return inventory


# =====================================================
# MAIN DATA PIPELINE
# =====================================================
def run_with_data(

    demand_df: pd.DataFrame,

    inventory_df: pd.DataFrame,

    num_days=3,

    store_master_df=None
):

    # =====================================================
    # STORE MASTER LOGIC
    # =====================================================

    # -------------------------------------------------
    # Real Geo Mode
    # -------------------------------------------------
    if store_master_df is not None:

        stores = build_store_master(
            store_master_df
        )

    # -------------------------------------------------
    # Synthetic Fallback Mode
    # -------------------------------------------------
    else:

        unique_store_count = (
            demand_df["store_id"]
            .nunique()
        )

        stores = generate_stores(
            unique_store_count
        )

    # =====================================================
    # DISTANCE COMPUTATION
    # =====================================================
    dist = compute_distance_matrix(
        stores
    )

    mask = compute_transfer_mask(
        dist,
        settings.MAX_DISTANCE_KM
    )

    # =====================================================
    # INVENTORY
    # =====================================================
    inventory = inventory_df.copy()

    all_logs = []

    # =====================================================
    # DAY LOOP
    # =====================================================
    for day in range(num_days):

        demand = demand_df.copy()

        # -------------------------------------------------
        # Inventory Simulation
        # -------------------------------------------------
        results, ending_inventory = (
            simulate_inventory(
                demand,
                inventory
            )
        )

        # -------------------------------------------------
        # Priority
        # -------------------------------------------------
        priority_df = compute_priority(
            ending_inventory
        )

        # -------------------------------------------------
        # Replenishment
        # -------------------------------------------------
        replenishment = (
            generate_replenishment_plan(
                ending_inventory
            )
        )

        # -------------------------------------------------
        # Metrics
        # -------------------------------------------------
        metrics = compute_metrics(
            results
        )

        # -------------------------------------------------
        # Surplus / Deficit
        # -------------------------------------------------
        surplus, deficit = (
            identify_surplus_deficit(
                ending_inventory,
                threshold=(
                    settings
                    .SURPLUS_THRESHOLD
                )
            )
        )

        # -------------------------------------------------
        # Transfers
        # -------------------------------------------------
        transfers = generate_transfer_plan(
            surplus,
            deficit,
            dist,
            mask
        )

        # =====================================================
        # EXPLAINABILITY
        # =====================================================
        explain_dict = {}

        if len(transfers) > 0:

            for _, row in transfers.iterrows():

                sku = row["sku_id"]

                if sku not in explain_dict:

                    explain_dict[sku] = {

                        "sku_id": sku,

                        "events": []
                    }

                # -----------------------------------------
                # Source Stock
                # -----------------------------------------
                source_stock_before = (
                    ending_inventory.loc[
                        (
                            ending_inventory[
                                "store_id"
                            ]
                            ==
                            row["from_store"]
                        )
                        &
                        (
                            ending_inventory[
                                "sku_id"
                            ]
                            ==
                            sku
                        ),
                        "stock"
                    ].iloc[0]
                )

                # -----------------------------------------
                # Destination Stock
                # -----------------------------------------
                destination_stock_before = (
                    ending_inventory.loc[
                        (
                            ending_inventory[
                                "store_id"
                            ]
                            ==
                            row["to_store"]
                        )
                        &
                        (
                            ending_inventory[
                                "sku_id"
                            ]
                            ==
                            sku
                        ),
                        "stock"
                    ].iloc[0]
                )

                # -----------------------------------------
                # Cost Logic
                # -----------------------------------------
                transfer_cost = round(
                    row["quantity"]
                    *
                    row["distance_km"],
                    2
                )

                stockout_risk_cost = int(
                    row["quantity"] * 10
                )

                # -----------------------------------------
                # Future Context
                # -----------------------------------------
                future_context = {

                    "inbound_inventory": 0,

                    "constraints": []
                }

                # -----------------------------------------
                # Decision Reason
                # -----------------------------------------
                decision_reason = (
                    "TRANSFER_THRESHOLD_BREACH"
                )

                # -----------------------------------------
                # Event Append
                # -----------------------------------------
                explain_dict[sku]["events"].append({

                    "event_type": "TRANSFER",

                    "from_store": (
                        row["from_store"]
                    ),

                    "to_store": (
                        row["to_store"]
                    ),

                    "source_stock_before": int(
                        source_stock_before
                    ),

                    "destination_stock_before": int(
                        destination_stock_before
                    ),

                    "threshold": int(
                        settings
                        .SURPLUS_THRESHOLD
                    ),

                    "quantity": int(
                        row["quantity"]
                    ),

                    "distance_km": round(
                        float(
                            row["distance_km"]
                        ),
                        2
                    ),

                    "cost": {

                        "transfer_cost": (
                            transfer_cost
                        ),

                        "stockout_risk_cost": (
                            stockout_risk_cost
                        )
                    },

                    "decision_reason": (
                        decision_reason
                    ),

                    "future_context": (
                        future_context
                    )
                })

        # =====================================================
        # EXPLAIN LIST
        # =====================================================
        explain_list = list(
            explain_dict.values()
        )

        # =====================================================
        # APPLY DECISIONS
        # =====================================================
        inventory = apply_transfers(
            ending_inventory,
            transfers
        )

        inventory = apply_replenishment(
            inventory,
            replenishment
        )

        # =====================================================
        # TOP PRIORITY
        # =====================================================
        top_priority = priority_df.head(3)[

            ["store_id", "sku_id", "stock"]
        ]

        # =====================================================
        # FINAL LOG
        # =====================================================
        all_logs.append({

            "day": day + 1,

            "transfers": transfers,

            "metrics": metrics,

            "top_priority": top_priority,

            "explain": explain_list,

            "stores": stores
        })

    return all_logs
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import streamlit as st
import pandas as pd


# =====================================================
# REASON MAPPING
# =====================================================
REASON_MAP = {

    "TRANSFER_THRESHOLD_BREACH": (
        "Destination inventory breached threshold. "
        "Transfer cost was lower than stockout risk."
    )
}


# =====================================================
# MAIN
# =====================================================
def main() -> None:

    st.set_page_config(
        page_title="StockPilot",
        page_icon="Q",
        layout="wide",
    )

    st.title("StockPilot")

    st.caption(
        "AI-powered inventory and transfer optimization 🚀"
    )

    st.divider()

    # =====================================================
    # DATA INPUT MODE
    # =====================================================
    st.subheader("Data Input")

    input_mode = st.radio(
        "Select Mode",
        [
            "Simulation Mode",
            "Upload Data Mode"
        ]
    )

    uploaded_demand = None
    uploaded_inventory = None

    demand_df = None
    inventory_df = None

    # =====================================================
    # UPLOAD MODE
    # =====================================================
    if input_mode == "Upload Data Mode":

        st.markdown("### Upload Files")

        # -------------------------------------------------
        # Templates
        # -------------------------------------------------
        st.markdown("#### Download Templates")

        demand_template = pd.DataFrame({

            "store_id": ["S1", "S1", "S2"],

            "sku_id": ["SKU1", "SKU2", "SKU1"],

            "demand": [10, 5, 8]
        })

        inventory_template = pd.DataFrame({

            "store_id": ["S1", "S1", "S2"],

            "sku_id": ["SKU1", "SKU2", "SKU1"],

            "stock": [20, 3, 15]
        })

        col1, col2 = st.columns(2)

        col1.download_button(
            "Download Demand Template",
            demand_template.to_csv(index=False),
            file_name="demand_template.csv"
        )

        col2.download_button(
            "Download Inventory Template",
            inventory_template.to_csv(index=False),
            file_name="inventory_template.csv"
        )

        # -------------------------------------------------
        # Uploaders
        # -------------------------------------------------
        uploaded_demand = st.file_uploader(
            "Upload Demand CSV",
            type=["csv"]
        )

        uploaded_inventory = st.file_uploader(
            "Upload Inventory CSV",
            type=["csv"]
        )

        st.info(
            """
            Expected Format:

            Demand:
            store_id, sku_id, demand

            Inventory:
            store_id, sku_id, stock
            """
        )

        # =====================================================
        # READ + VALIDATE
        # =====================================================
        if uploaded_demand and uploaded_inventory:

            uploaded_demand.seek(0)
            uploaded_inventory.seek(0)

            demand_df = pd.read_csv(
                uploaded_demand
            )

            inventory_df = pd.read_csv(
                uploaded_inventory
            )

            # -------------------------------------------------
            # Size Guard
            # -------------------------------------------------
            max_rows = 200000

            if (
                len(demand_df) > max_rows or
                len(inventory_df) > max_rows
            ):

                st.error(
                    f"Files too large. "
                    f"Limit is {max_rows} rows."
                )

                return

            # -------------------------------------------------
            # Type Validation
            # -------------------------------------------------
            try:

                demand_df["demand"] = pd.to_numeric(
                    demand_df["demand"]
                )

                inventory_df["stock"] = pd.to_numeric(
                    inventory_df["stock"]
                )

            except Exception:

                st.error(
                    "Demand/Stock columns must be numeric."
                )

                return

            # -------------------------------------------------
            # Dataset Summary
            # -------------------------------------------------
            st.subheader("Dataset Summary")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Stores",
                demand_df["store_id"].nunique()
            )

            c2.metric(
                "SKUs",
                demand_df["sku_id"].nunique()
            )

            c3.metric(
                "Rows",
                len(demand_df)
            )

            st.divider()

            # -------------------------------------------------
            # Preview
            # -------------------------------------------------
            st.subheader("Preview")

            col1, col2 = st.columns(2)

            with col1:

                st.write("Demand Sample")

                st.dataframe(
                    demand_df.head(5),
                    use_container_width=True
                )

            with col2:

                st.write("Inventory Sample")

                st.dataframe(
                    inventory_df.head(5),
                    use_container_width=True
                )

    # =====================================================
    # SIMULATION MODE
    # =====================================================
    if input_mode == "Simulation Mode":

        st.subheader("Simulation Inputs")

        col1, col2, col3 = st.columns(3)

        num_stores = col1.slider(
            "Stores",
            2,
            20,
            5
        )

        num_skus = col2.slider(
            "SKUs",
            5,
            50,
            10
        )

        num_days = col3.slider(
            "Days",
            1,
            7,
            3
        )

    else:

        st.subheader("Run Settings")

        num_days = st.slider(
            "Simulation Days",
            1,
            7,
            3
        )

    st.divider()

    # =====================================================
    # RUN BUTTON
    # =====================================================
    run_clicked = st.button(

        "Run StockPilot",

        disabled=(

            input_mode == "Upload Data Mode"

            and not (
                uploaded_demand and
                uploaded_inventory
            )
        )
    )

    # =====================================================
    # RUN
    # =====================================================
    if run_clicked:

        try:

            with st.spinner("Running..."):

                # -------------------------------------------------
                # Upload Mode
                # -------------------------------------------------
                if input_mode == "Upload Data Mode":

                    from pipelines.data_pipeline import (
                        run_with_data
                    )

                    logs = run_with_data(
                        demand_df,
                        inventory_df,
                        num_days
                    )

                # -------------------------------------------------
                # Simulation Mode
                # -------------------------------------------------
                else:

                    from pipelines.simulation_pipeline import (
                        run_simulation
                    )

                    logs = run_simulation(
                        num_stores,
                        num_skus,
                        num_days
                    )

        except Exception as e:

            st.error(
                "Error during execution"
            )

            st.text(str(e))

            return

        st.success("Run completed!")

        # =====================================================
        # DISPLAY
        # =====================================================
        all_metrics = []
        all_transfers = []

        for day_log in logs:

            st.markdown(
                f"## Day {day_log['day']}"
            )

            metrics = day_log["metrics"]

            metrics_row = metrics.copy()

            metrics_row["day"] = (
                day_log["day"]
            )

            all_metrics.append(metrics_row)

            # =====================================================
            # METRICS
            # =====================================================
            st.metric(
                "Efficiency Score",
                metrics["efficiency_score"]
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Stockout %",
                f"{metrics['stockout_pct']*100:.2f}%"
            )

            c2.metric(
                "Fill Rate",
                f"{metrics['fill_rate']*100:.2f}%"
            )

            c3.metric(
                "Demand",
                metrics["total_demand"]
            )

            c4.metric(
                "Fulfilled",
                metrics["total_fulfilled"]
            )

            st.divider()

            # =====================================================
            # TOP PRIORITY
            # =====================================================
            st.subheader("Top Priority")

            st.dataframe(
                day_log["top_priority"],
                use_container_width=True
            )

            st.divider()

            # =====================================================
            # TRANSFERS
            # =====================================================
            st.subheader("Transfers")

            transfers = day_log["transfers"]

            if len(transfers) > 0:

                transfer_copy = transfers.copy()

                transfer_copy["day"] = (
                    day_log["day"]
                )

                all_transfers.append(
                    transfer_copy
                )

                st.dataframe(
                    transfers,
                    use_container_width=True
                )

            else:

                st.info(
                    "No transfers required"
                )

            st.divider()

            # =====================================================
            # EXPLAINABILITY
            # =====================================================
            explain_data = day_log.get(
                "explain",
                []
            )

            if len(explain_data) > 0:

                st.subheader(
                    "Explainability "
                    "(Top Impact SKUs)"
                )

                # -------------------------------------------------
                # Impact Ranking
                # -------------------------------------------------
                scored_explanations = []

                for sku_block in explain_data:

                    total_impact = 0

                    for event in sku_block["events"]:

                        total_impact += (
                            event["quantity"] *
                            event["cost"][
                                "stockout_risk_cost"
                            ]
                        )

                    scored_explanations.append({

                        "sku_id": sku_block["sku_id"],

                        "impact": total_impact,

                        "events": sku_block["events"]
                    })

                # -------------------------------------------------
                # Sort Descending
                # -------------------------------------------------
                scored_explanations = sorted(

                    scored_explanations,

                    key=lambda x: x["impact"],

                    reverse=True
                )

                # -------------------------------------------------
                # Top 5 Only
                # -------------------------------------------------
                top_explanations = (
                    scored_explanations[:5]
                )

                # =====================================================
                # RENDER
                # =====================================================
                for sku_block in top_explanations:

                    sku = sku_block["sku_id"]

                    impact = sku_block["impact"]

                    with st.expander(

                        f"{sku} | Impact Score: {impact}",

                        expanded=False
                    ):

                        for event in sku_block["events"]:

                            st.markdown(
                                f"""
                                ### Transfer

                                **Route:**  
                                {event['from_store']}
                                →
                                {event['to_store']}

                                **Quantity:**  
                                {event['quantity']}

                                **Distance:**  
                                {event['distance_km']} km

                                **Source Stock Before:**  
                                {event['source_stock_before']}

                                **Destination Stock Before:**  
                                {event['destination_stock_before']}

                                **Threshold:**  
                                {event['threshold']}

                                ### Cost Analysis

                                **Transfer Cost:**  
                                {event['cost']['transfer_cost']}

                                **Stockout Risk Cost:**  
                                {event['cost']['stockout_risk_cost']}

                                ### Reason

                                {
                                    REASON_MAP.get(
                                        event[
                                            'decision_reason'
                                        ],
                                        event[
                                            'decision_reason'
                                        ]
                                    )
                                }
                                """
                            )

                            st.divider()

            st.divider()

        # =====================================================
        # DOWNLOADS
        # =====================================================
        st.subheader("Download Results")

        col1, col2 = st.columns(2)

        if len(all_metrics) > 0:

            metrics_df = pd.DataFrame(
                all_metrics
            )

            col1.download_button(
                "Download Metrics CSV",
                metrics_df.to_csv(index=False),
                file_name="metrics.csv",
                mime="text/csv"
            )

        if len(all_transfers) > 0:

            transfers_df = pd.concat(
                all_transfers
            )

            col2.download_button(
                "Download Transfers CSV",
                transfers_df.to_csv(index=False),
                file_name="transfers.csv",
                mime="text/csv"
            )


# =====================================================
# ENTRY
# =====================================================
if __name__ == "__main__":
    main()
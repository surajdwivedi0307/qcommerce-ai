
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

def main() -> None:

    st.set_page_config(
        page_title="StockPilot",
        page_icon="Q",
        layout="wide",
    )

    st.title("StockPilot")
    st.caption("AI-powered inventory and transfer optimization 🚀")

    st.divider()

    # -----------------------------
    # DATA INPUT MODE
    # -----------------------------
    st.subheader("Data Input")

    input_mode = st.radio(
        "Select Mode",
        ["Simulation Mode", "Upload Data Mode"]
    )

    uploaded_demand = None
    uploaded_inventory = None

    if input_mode == "Upload Data Mode":
        st.markdown("### Upload Files")

        # Templates
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

        with col1:
            st.download_button(
                "Download Demand Template",
                demand_template.to_csv(index=False),
                file_name="demand_template.csv",
                mime="text/csv"
            )

        with col2:
            st.download_button(
                "Download Inventory Template",
                inventory_template.to_csv(index=False),
                file_name="inventory_template.csv",
                mime="text/csv"
            )

        st.markdown("#### Upload Your Data")

        uploaded_demand = st.file_uploader("Upload Demand CSV", type=["csv"])
        uploaded_inventory = st.file_uploader("Upload Inventory CSV", type=["csv"])

        st.info("""
        Expected Format:

        Demand CSV:
        - store_id, sku_id, demand

        Inventory CSV:
        - store_id, sku_id, stock
        """)

        # Upload Analytics
        if uploaded_demand and uploaded_inventory:
            uploaded_demand.seek(0)
            uploaded_inventory.seek(0)

            demand_df = pd.read_csv(uploaded_demand)

            num_stores = demand_df["store_id"].nunique()
            num_skus = demand_df["sku_id"].nunique()

            st.subheader("Dataset Summary")

            c1, c2, c3 = st.columns(3)
            c1.metric("Stores", num_stores)
            c2.metric("SKUs", num_skus)
            c3.metric("Demand Rows", len(demand_df))

            st.divider()

    # -----------------------------
    # SIMULATION INPUTS
    # -----------------------------
    if input_mode == "Simulation Mode":
        st.subheader("Simulation Inputs")

        col1, col2, col3 = st.columns(3)

        num_stores = col1.slider("Number of Stores", 2, 20, 5)
        num_skus = col2.slider("Number of SKUs", 5, 50, 10)
        num_days = col3.slider("Simulation Days", 1, 7, 3)

    else:
        st.subheader("Run Settings")
        num_days = st.slider("Simulation Days", 1, 7, 3)

    st.divider()

    # -----------------------------
    # RUN
    # -----------------------------
    if st.button("Run StockPilot"):

        with st.spinner("Running..."):

            if input_mode == "Upload Data Mode" and uploaded_demand and uploaded_inventory:
                from pipelines.data_pipeline import run_with_data
                from utils.validation_utils import validate_demand, validate_inventory

                uploaded_demand.seek(0)
                uploaded_inventory.seek(0)

                demand_df = pd.read_csv(uploaded_demand)
                inventory_df = pd.read_csv(uploaded_inventory)

                valid_demand, msg1 = validate_demand(demand_df)
                valid_inventory, msg2 = validate_inventory(inventory_df)

                if not valid_demand:
                    st.error(msg1)
                    return

                if not valid_inventory:
                    st.error(msg2)
                    return

                logs = run_with_data(demand_df, inventory_df, num_days)

            else:
                from pipelines.simulation_pipeline import run_simulation
                logs = run_simulation(num_stores, num_skus, num_days)

        st.success("Run completed!")

        # -----------------------------
        # DISPLAY + DOWNLOAD (FIXED)
        # -----------------------------
        all_transfers = []
        all_metrics = []

        for day_log in logs:
            st.markdown(f"## Day {day_log['day']}")

            metrics = day_log["metrics"]

            metrics_row = metrics.copy()
            metrics_row["day"] = day_log["day"]
            all_metrics.append(metrics_row)

            st.metric("Network Efficiency Score", f"{metrics['efficiency_score']}")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Stockout %", f"{metrics['stockout_pct']*100:.2f}%")
            c2.metric("Fill Rate", f"{metrics['fill_rate']*100:.2f}%")
            c3.metric("Total Demand", metrics["total_demand"])
            c4.metric("Fulfilled", metrics["total_fulfilled"])

            st.divider()

            st.subheader("Top Priority")
            st.dataframe(day_log["top_priority"], use_container_width=True)

            st.subheader("Transfers")

            transfers = day_log["transfers"]

            if len(transfers) > 0:
                transfers_copy = transfers.copy()
                transfers_copy["day"] = day_log["day"]
                all_transfers.append(transfers_copy)

                st.dataframe(transfers, use_container_width=True)
            else:
                st.info("No transfers required")

            st.divider()

        # -----------------------------
        # DOWNLOAD SECTION
        # -----------------------------
        st.subheader("Download Results")

        col1, col2 = st.columns(2)

        if len(all_metrics) > 0:
            metrics_df = pd.DataFrame(all_metrics)

            col1.download_button(
                "Download Metrics CSV",
                metrics_df.to_csv(index=False),
                file_name="metrics.csv",
                mime="text/csv"
            )

        if len(all_transfers) > 0:
            transfers_df = pd.concat(all_transfers)

            col2.download_button(
                "Download Transfers CSV",
                transfers_df.to_csv(index=False),
                file_name="transfers.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()
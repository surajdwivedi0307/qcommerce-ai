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

    demand_df = None
    inventory_df = None

    # -----------------------------
    # UPLOAD MODE
    # -----------------------------
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

        uploaded_demand = st.file_uploader("Upload Demand CSV", type=["csv"])
        uploaded_inventory = st.file_uploader("Upload Inventory CSV", type=["csv"])

        st.info("""
        Expected Format:
        Demand → store_id, sku_id, demand  
        Inventory → store_id, sku_id, stock
        """)

        # -----------------------------
        # READ + VALIDATE (SAFE)
        # -----------------------------
        if uploaded_demand and uploaded_inventory:

            uploaded_demand.seek(0)
            uploaded_inventory.seek(0)

            demand_df = pd.read_csv(uploaded_demand)
            inventory_df = pd.read_csv(uploaded_inventory)

            # Size guard
            max_rows = 200000
            if len(demand_df) > max_rows or len(inventory_df) > max_rows:
                st.error(f"Files too large. Limit is {max_rows} rows.")
                return

            # Type validation
            try:
                demand_df["demand"] = pd.to_numeric(demand_df["demand"])
                inventory_df["stock"] = pd.to_numeric(inventory_df["stock"])
            except Exception:
                st.error("Demand/Stock must be numeric")
                return

            # Summary
            st.subheader("Dataset Summary")

            c1, c2, c3 = st.columns(3)
            c1.metric("Stores", demand_df["store_id"].nunique())
            c2.metric("SKUs", demand_df["sku_id"].nunique())
            c3.metric("Rows", len(demand_df))

            # Preview
            st.subheader("Preview")
            col1, col2 = st.columns(2)

            col1.dataframe(demand_df.head(5))
            col2.dataframe(inventory_df.head(5))

    # -----------------------------
    # SIMULATION INPUTS
    # -----------------------------
    if input_mode == "Simulation Mode":
        st.subheader("Simulation Inputs")

        col1, col2, col3 = st.columns(3)

        num_stores = col1.slider("Stores", 2, 20, 5)
        num_skus = col2.slider("SKUs", 5, 50, 10)
        num_days = col3.slider("Days", 1, 7, 3)

    else:
        num_days = st.slider("Simulation Days", 1, 7, 3)

    st.divider()

    # -----------------------------
    # RUN BUTTON
    # -----------------------------
    run_clicked = st.button(
        "Run StockPilot",
        disabled=(input_mode == "Upload Data Mode" and not (uploaded_demand and uploaded_inventory))
    )

    if run_clicked:

        try:
            with st.spinner("Running..."):

                if input_mode == "Upload Data Mode":
                    from pipelines.data_pipeline import run_with_data
                    logs = run_with_data(demand_df, inventory_df, num_days)

                else:
                    from pipelines.simulation_pipeline import run_simulation
                    logs = run_simulation(num_stores, num_skus, num_days)

        except Exception as e:
            st.error("Error during execution")
            st.text(str(e))
            return

        st.success("Run completed!")

        # -----------------------------
        # DISPLAY + DOWNLOAD
        # -----------------------------
        all_metrics = []
        all_transfers = []

        for day_log in logs:
            st.markdown(f"## Day {day_log['day']}")

            metrics = day_log["metrics"]

            metrics_row = metrics.copy()
            metrics_row["day"] = day_log["day"]
            all_metrics.append(metrics_row)

            st.metric("Efficiency Score", metrics["efficiency_score"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Stockout %", f"{metrics['stockout_pct']*100:.2f}%")
            c2.metric("Fill Rate", f"{metrics['fill_rate']*100:.2f}%")
            c3.metric("Demand", metrics["total_demand"])
            c4.metric("Fulfilled", metrics["total_fulfilled"])

            st.subheader("Transfers")

            if len(day_log["transfers"]) > 0:
                df = day_log["transfers"].copy()
                df["day"] = day_log["day"]
                all_transfers.append(df)
                st.dataframe(df)
            else:
                st.info("No transfers")

        st.subheader("Download")

        if all_metrics:
            st.download_button(
                "Download Metrics",
                pd.DataFrame(all_metrics).to_csv(index=False),
                "metrics.csv"
            )

        if all_transfers:
            st.download_button(
                "Download Transfers",
                pd.concat(all_transfers).to_csv(index=False),
                "transfers.csv"
            )


if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd


def main() -> None:

    st.set_page_config(
        page_title="StockPilot",
        page_icon="Q",
        layout="wide",
    )

    # -----------------------------
    # Header
    # -----------------------------
    st.title("StockPilot")
    st.caption("AI-powered inventory and transfer optimization 🚀")

    st.divider()

    # -----------------------------
    # Simulation Section
    # -----------------------------
    st.subheader("Run Simulation")

    if st.button("Run Simulation"):
        from pipelines.simulation_pipeline import run_simulation

        with st.spinner("Running simulation..."):
            logs = run_simulation()

        st.success("Simulation completed!")

        # -----------------------------
        # Trend Data Preparation
        # -----------------------------
        trend_data = []

        for day_log in logs:
            m = day_log["metrics"]
            trend_data.append({
                "day": day_log["day"],
                "stockout_pct": m["stockout_pct"],
                "fill_rate": m["fill_rate"]
            })

        trend_df = pd.DataFrame(trend_data)

        # -----------------------------
        # Trend Charts
        # -----------------------------
        st.subheader("Performance Trend")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Stockout %")
            st.line_chart(trend_df.set_index("day")["stockout_pct"])

        with col2:
            st.write("Fill Rate")
            st.line_chart(trend_df.set_index("day")["fill_rate"])

        st.divider()

        # -----------------------------
        # Day-wise Breakdown
        # -----------------------------
        for day_log in logs:
            st.markdown(f"## Day {day_log['day']}")

            metrics = day_log["metrics"]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Stockout %", f"{metrics['stockout_pct']*100:.2f}%")
            col2.metric("Fill Rate", f"{metrics['fill_rate']*100:.2f}%")
            col3.metric("Total Demand", metrics["total_demand"])
            col4.metric("Fulfilled", metrics["total_fulfilled"])

            st.divider()

            # Priority
            st.subheader("Top Priority (Critical SKUs)")
            st.dataframe(day_log["top_priority"], use_container_width=True)

            # Transfers
            st.subheader("Transfers Plan")

            transfers = day_log["transfers"]

            if len(transfers) > 0:
                st.dataframe(transfers, use_container_width=True)
            else:
                st.info("No transfers required")

            st.divider()


if __name__ == "__main__":
    main()
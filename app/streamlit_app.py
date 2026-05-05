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
    # Inputs
    # -----------------------------
    st.subheader("Simulation Inputs")

    col1, col2, col3 = st.columns(3)

    num_stores = col1.slider("Number of Stores", 2, 20, 5)
    num_skus = col2.slider("Number of SKUs", 5, 50, 10)
    num_days = col3.slider("Simulation Days", 1, 7, 3)

    st.divider()

    # -----------------------------
    # Run
    # -----------------------------
    if st.button("Run Simulation"):

        from pipelines.simulation_pipeline import run_simulation

        with st.spinner("Running simulation..."):
            logs = run_simulation(num_stores, num_skus, num_days)

        st.success("Simulation completed!")

        # -----------------------------
        # Trend
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

        st.subheader("Performance Trend")

        col1, col2 = st.columns(2)

        with col1:
            st.line_chart(trend_df.set_index("day")["stockout_pct"])

        with col2:
            st.line_chart(trend_df.set_index("day")["fill_rate"])

        st.divider()

        # -----------------------------
        # Day Breakdown
        # -----------------------------
        for day_log in logs:
            st.markdown(f"## Day {day_log['day']}")

            metrics = day_log["metrics"]

            # -----------------------------
            # NEW → Efficiency Highlight
            # -----------------------------
            st.metric(
                "Network Efficiency Score",
                f"{metrics['efficiency_score']}"
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Stockout %", f"{metrics['stockout_pct']*100:.2f}%")
            c2.metric("Fill Rate", f"{metrics['fill_rate']*100:.2f}%")
            c3.metric("Total Demand", metrics["total_demand"])
            c4.metric("Fulfilled", metrics["total_fulfilled"])

            st.divider()

            st.subheader("Top Priority")
            st.dataframe(day_log["top_priority"], use_container_width=True)

            st.subheader("Transfers")

            if len(day_log["transfers"]) > 0:
                st.dataframe(day_log["transfers"], use_container_width=True)
            else:
                st.info("No transfers required")

            st.divider()


if __name__ == "__main__":
    main()
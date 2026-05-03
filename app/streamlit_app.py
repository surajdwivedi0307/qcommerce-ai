import streamlit as st

from config import get_settings


def main() -> None:
    settings = get_settings()

    st.set_page_config(
        page_title=settings.app_name,
        page_icon="Q",
        layout="wide",
    )

    st.title(settings.app_name)
    st.caption("Operational cockpit for demand, inventory, delivery, and pricing intelligence.")

    metric_columns = st.columns(4)
    metric_columns[0].metric("Delivery SLA", f"{settings.default_delivery_sla_minutes} min")
    metric_columns[1].metric("Service Radius", f"{settings.default_service_radius_km:.1f} km")
    metric_columns[2].metric("Environment", settings.app_env)
    metric_columns[3].metric("Debug", "On" if settings.debug else "Off")

    st.divider()

    st.subheader("System Modules")
    modules = {
        "Data": "Ingest, validate, and transform operational data.",
        "Models": "Forecast demand, classify risk, and score recommendations.",
        "Agents": "Coordinate planning workflows and decision support.",
        "Optimization": "Route, allocate inventory, and tune fulfillment decisions.",
        "Pipelines": "Orchestrate repeatable data and model workflows.",
    }

    for name, description in modules.items():
        with st.expander(name, expanded=name == "Data"):
            st.write(description)


if __name__ == "__main__":
    main()

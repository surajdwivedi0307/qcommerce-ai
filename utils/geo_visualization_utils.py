import pandas as pd
import pydeck as pdk


# =====================================================
# BUILD STORE LOOKUP
# =====================================================
def build_store_lookup(
    stores_df
):

    return (
        stores_df[
            [
                "store_id",
                "lat",
                "lon"
            ]
        ]
        .drop_duplicates()
        .set_index("store_id")
    )


# =====================================================
# BUILD TRANSFER GEO DATAFRAME
# =====================================================
def build_transfer_geo_dataframe(

    transfers_df,

    stores_df
):

    # -------------------------------------------------
    # Empty Protection
    # -------------------------------------------------
    if len(transfers_df) == 0:

        return pd.DataFrame()

    # -------------------------------------------------
    # Store Lookup
    # -------------------------------------------------
    store_lookup = build_store_lookup(
        stores_df
    )

    geo_rows = []

    # =====================================================
    # TRANSFER LOOP
    # =====================================================
    for _, row in transfers_df.iterrows():

        from_store = row["from_store"]

        to_store = row["to_store"]

        # -------------------------------------------------
        # Missing Store Protection
        # -------------------------------------------------
        if (
            from_store not in store_lookup.index
            or
            to_store not in store_lookup.index
        ):

            continue

        # -------------------------------------------------
        # Coordinates
        # -------------------------------------------------
        from_lat = (
            store_lookup.loc[
                from_store,
                "lat"
            ]
        )

        from_lon = (
            store_lookup.loc[
                from_store,
                "lon"
            ]
        )

        to_lat = (
            store_lookup.loc[
                to_store,
                "lat"
            ]
        )

        to_lon = (
            store_lookup.loc[
                to_store,
                "lon"
            ]
        )

        # -------------------------------------------------
        # Arc Row
        # -------------------------------------------------
        geo_rows.append({

            "sku_id": row["sku_id"],

            "from_store": from_store,

            "to_store": to_store,

            "quantity": row["quantity"],

            "distance_km": row["distance_km"],

            "from_lat": from_lat,

            "from_lon": from_lon,

            "to_lat": to_lat,

            "to_lon": to_lon,
        })

    return pd.DataFrame(
        geo_rows
    )


# =====================================================
# GENERATE TRANSFER MAP
# =====================================================
def generate_transfer_map(

    geo_df,

    stores_df
):

    # -------------------------------------------------
    # Empty Protection
    # -------------------------------------------------
    if len(stores_df) == 0:

        return None

    # =====================================================
    # STORE LAYER
    # =====================================================
    store_layer = pdk.Layer(

        "ScatterplotLayer",

        data=stores_df,

        get_position="[lon, lat]",

        get_radius=800,

        pickable=True,

        opacity=0.8,

        stroked=True,

        filled=True,

        radius_scale=1,

        radius_min_pixels=5,

        radius_max_pixels=15,

        line_width_min_pixels=1,

        get_fill_color=[0, 128, 255],

        get_line_color=[255, 255, 255],
    )

    # =====================================================
    # TRANSFER ARC LAYER
    # =====================================================
    arc_layer = pdk.Layer(

        "ArcLayer",

        data=geo_df,

        get_source_position="[from_lon, from_lat]",

        get_target_position="[to_lon, to_lat]",

        get_source_color=[255, 140, 0],

        get_target_color=[0, 200, 100],

        pickable=True,

        auto_highlight=True,

        width_scale=1,

        get_width="quantity",
    )

    # =====================================================
    # VIEW STATE
    # =====================================================
    center_lat = stores_df["lat"].mean()

    center_lon = stores_df["lon"].mean()

    view_state = pdk.ViewState(

        latitude=center_lat,

        longitude=center_lon,

        zoom=4,

        pitch=30,
    )

    # =====================================================
    # TOOLTIP
    # =====================================================
    tooltip = {

        "html": """

        <b>SKU:</b> {sku_id} <br/>

        <b>Route:</b>
        {from_store} → {to_store} <br/>

        <b>Quantity:</b> {quantity} <br/>

        <b>Distance:</b> {distance_km} km
        """,

        "style": {

            "backgroundColor": "black",

            "color": "white"
        }
    }

    # =====================================================
    # DECK
    # =====================================================
    deck = pdk.Deck(

        layers=[
            store_layer,
            arc_layer
        ],

        initial_view_state=view_state,

        tooltip=tooltip,

        map_style="mapbox://styles/mapbox/dark-v10"
    )

    return deck
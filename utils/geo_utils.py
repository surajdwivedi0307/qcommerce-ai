import numpy as np
import pandas as pd

np.random.seed(42)

CITY_COORDS = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Hyderabad": (17.3850, 78.4867),
}


def generate_stores(num_stores_per_city=20):
    stores = []
    store_id = 1

    for city, (lat, lon) in CITY_COORDS.items():
        for _ in range(num_stores_per_city):
            stores.append({
                "store_id": f"S{store_id}",
                "city": city,
                "lat": lat + np.random.uniform(-0.05, 0.05),
                "lon": lon + np.random.uniform(-0.05, 0.05),
                "capacity": np.random.randint(500, 2000),
            })
            store_id += 1

    return pd.DataFrame(stores)


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


def compute_distance_matrix(stores_df):
    store_ids = stores_df["store_id"].values
    n = len(store_ids)

    distance_matrix = pd.DataFrame(
        np.zeros((n, n)),
        index=store_ids,
        columns=store_ids,
    )

    for i in range(n):
        for j in range(n):
            distance_matrix.iloc[i, j] = haversine_distance(
                stores_df.iloc[i]["lat"],
                stores_df.iloc[i]["lon"],
                stores_df.iloc[j]["lat"],
                stores_df.iloc[j]["lon"],
            )

    return distance_matrix
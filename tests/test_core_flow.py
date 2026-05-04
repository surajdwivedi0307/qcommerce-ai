def test_core_flow():
    from utils.geo_utils import generate_stores
    from utils.demand_utils import generate_sku_master, generate_hourly_demand
    from utils.inventory_utils import initialize_inventory, simulate_inventory

    stores = generate_stores(3)
    skus = generate_sku_master(3)

    demand = generate_hourly_demand(stores, skus, days=1)
    inventory = initialize_inventory(stores, skus)

    _, ending_inventory = simulate_inventory(demand, inventory)

    assert ending_inventory is not None
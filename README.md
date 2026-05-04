# StockPilot

StockPilot is an agentic AI system for optimizing inventory and network operations in q-commerce.

## 🚀 What it does

- Simulates demand across stores and SKUs
- Tracks inventory and stockouts
- Identifies surplus and deficit nodes
- Optimizes store-to-store transfers
- Uses an agent to make daily decisions

## 🧠 Architecture

Data → Simulation → Optimization → Agent → Output

## 📦 Project Structure

- `utils/` → core logic (geo, demand, inventory)
- `optimization/` → transfer optimization
- `agents/` → decision-making layer
- `pipelines/` → simulation loop
- `configs/` → system parameters
- `tests/` → validation tests
- `app/` → Streamlit UI

## ▶️ How to Run

### Run simulation

```bash
PYTHONPATH=. python
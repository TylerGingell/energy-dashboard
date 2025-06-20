
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Energy Revenue Dashboard")

# Input total consumption
total_volume = st.number_input("Total Consumption Volume (kWh)", min_value=0.0, value=100000.0)

# Slider for split
sleeved_pct = st.slider("Sleeved Volume (%)", 0, 100, 50)
sleeved_vol = total_volume * (sleeved_pct / 100)
grid_vol = total_volume - sleeved_vol

# Input export volume
export_vol = st.number_input("Exported Volume (kWh)", min_value=0.0, value=0.0)

# Input rates
private_rate = st.number_input("Private Market Rate (p/kWh)", min_value=0.0, value=10.0)
grid_rate = st.number_input("Grid Rate (p/kWh)", min_value=0.0, value=20.0)
spill_rate = st.number_input("Spill/Export Rate (p/kWh)", min_value=0.0, value=8.5)

# Calculate revenues
revenue_sleeved = sleeved_vol * private_rate / 100
revenue_grid = grid_vol * grid_rate / 100
revenue_export = export_vol * spill_rate / 100
total_revenue = revenue_sleeved + revenue_grid + revenue_export

# Display revenue breakdown
st.subheader("Revenue Breakdown")
st.write(f"Sleeved Volume: {sleeved_vol:.2f} kWh @ {private_rate}p → £{revenue_sleeved:.2f}")
st.write(f"Grid Volume: {grid_vol:.2f} kWh @ {grid_rate}p → £{revenue_grid:.2f}")
st.write(f"Export Volume: {export_vol:.2f} kWh @ {spill_rate}p → £{revenue_export:.2f}")
st.markdown("---")
st.write(f"**Total Revenue: £{total_revenue:.2f}**")

# Plotting
fig, ax = plt.subplots()
categories = ["Sleeved", "Grid", "Export"]
revenues = [revenue_sleeved, revenue_grid, revenue_export]
ax.bar(categories, revenues)
ax.set_ylabel("Revenue (£)")
ax.set_title("Revenue Breakdown")
st.pyplot(fig)

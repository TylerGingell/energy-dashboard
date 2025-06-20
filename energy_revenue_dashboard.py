import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Multi-MPAN Energy Revenue Dashboard", layout="wide")
st.title("📊 Multi-MPAN Energy Revenue Dashboard")

st.markdown("""
Type your MPAN data below. For each MPAN, enter:
- Total volume (kWh)
- Sleeved % (rest is grid)
- Export volume (kWh)
- Unit rates (p/kWh)
- Standing charge (£/day)
""")

# Default data for 2 MPANs
default_data = pd.DataFrame({
    "MPAN": ["1234567890123", "2345678901234"],
    "Total Volume (kWh)": [100000, 80000],
    "Sleeved %": [50, 40],
    "Export Volume (kWh)": [5000, 10000],
    "Sleeved Rate (p/kWh)": [10.0, 9.5],
    "Grid Rate (p/kWh)": [20.0, 19.8],
    "Export Rate (p/kWh)": [8.5, 8.0],
    "Standing Charge (£/day)": [0.25, 0.30]
})

edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

results = []
for _, row in edited_df.iterrows():
    mpan = row["MPAN"]
    total_volume = row["Total Volume (kWh)"]
    sleeved_pct = row["Sleeved %"]
    export_vol = row["Export Volume (kWh)"]

    # Rates
    private_rate = row["Sleeved Rate (p/kWh)"]
    grid_rate = row["Grid Rate (p/kWh)"]
    spill_rate = row["Export Rate (p/kWh)"]
    standing_daily = row["Standing Charge (£/day)"]

    # Calculations
    sleeved_vol = total_volume * (sleeved_pct / 100)
    grid_vol = total_volume - sleeved_vol
    revenue_sleeved = sleeved_vol * private_rate / 100
    revenue_grid = grid_vol * grid_rate / 100
    revenue_export = export_vol * spill_rate / 100
    standing_charge = standing_daily * 365
    total_revenue = revenue_sleeved + revenue_grid + revenue_export
    net_revenue = total_revenue - standing_charge

    results.append({
        "MPAN": mpan,
        "Sleeved Revenue (£)": revenue_sleeved,
        "Grid Revenue (£)": revenue_grid,
        "Export Revenue (£)": revenue_export,
        "Standing Charges (£)": standing_charge,
        "Net Revenue (£)": net_revenue
    })

results_df = pd.DataFrame(results)

st.subheader("📋 Revenue Summary by MPAN")
st.dataframe(results_df, use_container_width=True)

# Bar chart for net revenue
st.subheader("💰 Net Revenue Comparison")
fig, ax = plt.subplots()
ax.bar(results_df["MPAN"].astype(str), results_df["Net Revenue (£)"])
ax.set_ylabel("Net Revenue (£)")
ax.set_title("Net Revenue by MPAN")
st.pyplot(fig)


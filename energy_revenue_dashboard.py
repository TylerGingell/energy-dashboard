import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Branding color from UrbanChain logo
primary_color = "#00d2c6"

st.set_page_config(page_title="UrbanChain Energy Revenue Dashboard", layout="wide")
st.markdown(f"<h1 style='color:{primary_color};'>⚡ UrbanChain Energy Revenue Dashboard</h1>", unsafe_allow_html=True)

st.image("Logo.png", width=150)

st.markdown("""
Enter MPAN data below. For each MPAN, provide:
- Total volume (kWh)
- Sleeved % (rest is grid)
- Export volume (kWh)
- Total Generation (kWh)
- Unit rates (p/kWh)
- Standing charge (£/day)
""")

# Example data
default_data = pd.DataFrame({
    "MPAN": ["1234567890123", "2345678901234"],
    "Total Volume (kWh)": [100000, 80000],
    "Sleeved %": [50, 40],
    "Export Volume (kWh)": [5000, 10000],
    "Total Generation (kWh)": [105000, 90000],
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
    generation = row["Total Generation (kWh)"]

    # Rates
    private_rate = row["Sleeved Rate (p/kWh)"]
    grid_rate = row["Grid Rate (p/kWh)"]
    spill_rate = row["Export Rate (p/kWh)"]
    standing_daily = row["Standing Charge (£/day)"]

    # Calculations
    sleeved_vol = total_volume * (sleeved_pct / 100)
    grid_vol = total_volume - sleeved_vol
    spill_vol = max(generation - sleeved_vol, 0)
    match_pct = (sleeved_vol / generation) * 100 if generation else 0
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
        "Match %": round(match_pct, 2),
        "Spill Volume (kWh)": round(spill_vol, 2),
        "Net Revenue (£)": net_revenue
    })

results_df = pd.DataFrame(results)

st.subheader("📋 Revenue Summary by MPAN")
st.dataframe(results_df, use_container_width=True)

# Chart: Net Revenue
st.subheader("💰 Net Revenue by MPAN")
fig1, ax1 = plt.subplots()
ax1.bar(results_df["MPAN"].astype(str), results_df["Net Revenue (£)"], color=primary_color)
ax1.set_ylabel("Net Revenue (£)")
ax1.set_title("Net Revenue")
st.pyplot(fig1)

# Chart: Match %
st.subheader("🔁 Match % by MPAN")
fig2, ax2 = plt.subplots()
ax2.bar(results_df["MPAN"].astype(str), results_df["Match %"], color=primary_color)
ax2.set_ylabel("Match %")
ax2.set_ylim(0, 100)
ax2.set_title("Generation Matching (%)")
st.pyplot(fig2)



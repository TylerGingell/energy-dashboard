import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="UrbanChain Dashboard", layout="wide")
PRIMARY_COLOR = "#00d2c6"

st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>⚡ UrbanChain Dashboard – Manual Gen vs Grid Allocation</h1>", unsafe_allow_html=True)

st.sidebar.header("Rates")
private_rate = st.sidebar.number_input("Private Market Rate (p/kWh)", value=5.0)
uc_market_rate = st.sidebar.number_input("UC Market Rate (p/kWh)", value=8.5)

# Editable data
default_imports = pd.DataFrame({
    "MPAN": ["1050002056826", "1050002056827"],
    "Total Consumption (kWh)": [66841, 45000],
    "From Generation (kWh)": [1257, 1000],
    "From Grid (kWh)": [65585, 44000],
    "Tariff From Generation (p/kWh)": [15, 15],
    "Tariff From Grid (p/kWh)": [21, 21],
})

default_export = pd.DataFrame({
    "MPAN": ["1050002754336"],
    "Total Generation (kWh)": [244000]
})

import_df = st.data_editor(default_imports, num_rows="dynamic", use_container_width=True, key="import_editor")
export_df = st.data_editor(default_export, num_rows="dynamic", use_container_width=True, key="export_editor")

# Calculations
total_transferred = import_df["From Generation (kWh)"].sum()
total_generation = export_df["Total Generation (kWh)"].sum()
spilled = max(total_generation - total_transferred, 0)

allocation_results = []

for _, row in import_df.iterrows():
    mpan = row["MPAN"]
    cons = float(row["Total Consumption (kWh)"])
    from_gen = float(row["From Generation (kWh)"])
    from_grid = float(row["From Grid (kWh)"])
    gen_rate = float(row["Tariff From Generation (p/kWh)"])
    grid_rate = float(row["Tariff From Grid (p/kWh)"])
    warning = "⚠️" if from_gen + from_grid > cons else ""
    match_pct = (from_gen / cons) * 100 if cons > 0 else 0
    revenue_gen = from_gen * gen_rate / 100
    revenue_grid = from_grid * grid_rate / 100
    total_cost = revenue_gen + revenue_grid

    allocation_results.append({
        "MPAN": mpan,
        "Consumption (kWh)": cons,
        "From Gen (kWh)": from_gen,
        "From Grid (kWh)": from_grid,
        "Match %": round(match_pct, 2),
        "Gen Cost (£)": revenue_gen,
        "Grid Cost (£)": revenue_grid,
        "Total Cost (£)": total_cost,
        "⚠️": warning
    })

summary_df = pd.DataFrame(allocation_results)

private_revenue = total_transferred * private_rate / 100
uc_revenue = spilled * uc_market_rate / 100
total_export_revenue = private_revenue + uc_revenue

export_summary = pd.DataFrame([{
    "Generation Available (kWh)": total_generation,
    "Transferred to Consumers (kWh)": total_transferred,
    "Spilled to Grid (kWh)": spilled,
    "Private Market Revenue (£)": round(private_revenue, 2),
    "UC Market Revenue (£)": round(uc_revenue, 2),
    "Total Export Revenue (£)": round(total_export_revenue, 2)
}])

# Right-aligned KPI summary
st.markdown("## 🧾 Key Headlines")
left, right = st.columns([1, 3])
with left:
    st.metric("Total Generation", f"{total_generation:,.0f} kWh")
    st.metric("Total Consumption", f"{summary_df['Consumption (kWh)'].sum():,.0f} kWh")
    st.metric("Match %", f"{summary_df['Match %'].mean():.1f}%")
    st.metric("Generation Left Over", f"{spilled:,.0f} kWh")
    st.metric("Total Savings", f"£{(summary_df['Grid Cost (£)'].sum() - summary_df['Gen Cost (£)'].sum()):,.2f}")

# MPAN Filter
st.markdown("## 🔍 MPAN Filter")
mpan_options = ["All"] + sorted(summary_df["MPAN"].astype(str).unique().tolist())
selected_mpan = st.selectbox("Select MPAN to view details", mpan_options)

if selected_mpan != "All":
    filtered_df = summary_df[summary_df["MPAN"].astype(str) == selected_mpan]
else:
    filtered_df = summary_df

# Display tables
st.subheader("📊 Import MPAN Summary")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("📦 Export MPAN Summary")
st.dataframe(export_summary, use_container_width=True)






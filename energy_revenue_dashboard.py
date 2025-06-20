import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="UrbanChain Manual Allocation Dashboard", layout="wide")
PRIMARY_COLOR = "#00d2c6"

st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>⚡ UrbanChain Manual Consumption Allocation</h1>", unsafe_allow_html=True)

st.sidebar.header("Rates")
private_rate = st.sidebar.number_input("Private Market Rate (p/kWh)", value=5.0)
uc_market_rate = st.sidebar.number_input("UC Market Rate (p/kWh)", value=8.5)

st.header("📥 Input Data")

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

# Editable import and export tables
st.subheader("Import MPANs – Manual Split")
import_df = st.data_editor(default_imports, num_rows="dynamic", use_container_width=True)

st.subheader("Export MPAN – Total Generation")
export_df = st.data_editor(default_export, num_rows="dynamic", use_container_width=True)

# Calculate totals and validate
total_transferred = import_df["From Generation (kWh)"].sum()
total_generation = export_df["Total Generation (kWh)"].sum()
spilled = max(total_generation - total_transferred, 0)

# Compute import MPAN-level results
allocation_results = []

for _, row in import_df.iterrows():
    mpan = row["MPAN"]
    cons = float(row["Total Consumption (kWh)"])
    from_gen = float(row["From Generation (kWh)"])
    from_grid = float(row["From Grid (kWh)"])
    gen_rate = float(row["Tariff From Generation (p/kWh)"])
    grid_rate = float(row["Tariff From Grid (p/kWh)"])

    if from_gen + from_grid > cons:
        warning = "⚠️ Overallocated"
    else:
        warning = ""

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

# Export results
private_revenue = total_transferred * private_rate / 100
uc_revenue = spilled * uc_market_rate / 100
total_export_revenue = private_revenue + uc_revenue

export_results = {
    "Generation Available (kWh)": total_generation,
    "Transferred to Consumers (kWh)": total_transferred,
    "Spilled to Grid (kWh)": spilled,
    "Private Market Revenue (£)": round(private_revenue, 2),
    "UC Market Revenue (£)": round(uc_revenue, 2),
    "Total Export Revenue (£)": round(total_export_revenue, 2)
}

# Display tables
st.header("📊 Import MPAN Cost Summary")
st.dataframe(pd.DataFrame(allocation_results), use_container_width=True)

st.header("⚡ Export MPAN Revenue Summary")
st.dataframe(pd.DataFrame([export_results]), use_container_width=True)

# Plot
st.subheader("💰 Total Cost by Import MPAN")
plot_df = pd.DataFrame(allocation_results)
fig, ax = plt.subplots()
ax.bar(plot_df["MPAN"].astype(str), plot_df["Total Cost (£)"], color=PRIMARY_COLOR)
ax.set_ylabel("Total Cost (£)")
st.pyplot(fig)





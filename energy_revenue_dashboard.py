import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="UrbanChain Generation Allocation Dashboard", layout="wide")
PRIMARY_COLOR = "#00d2c6"

st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>⚡ UrbanChain Generation Allocation Dashboard</h1>", unsafe_allow_html=True)

st.sidebar.header("Settings")
private_rate = st.sidebar.number_input("Private Market Rate (p/kWh)", value=5.0)
uc_market_rate = st.sidebar.number_input("UC Market Rate (p/kWh)", value=8.5)

st.header("📥 Input Data")

# Sample Inputs
default_imports = pd.DataFrame({
    "MPAN": ["1050002056826", "1050002056827"],
    "Consumption (kWh)": [66841, 45000],
    "Tariff From Generation (p/kWh)": [15, 15],
    "Tariff From Grid (p/kWh)": [21, 21],
})

default_export = pd.DataFrame({
    "MPAN": ["1050002754336"],
    "Generation (kWh)": [244000],
})

# Editable tables
st.subheader("Import MPANs (Consumers)")
import_df = st.data_editor(default_imports, num_rows="dynamic", use_container_width=True)

st.subheader("Export MPAN (Generator)")
export_df = st.data_editor(default_export, num_rows="dynamic", use_container_width=True)

# Total available generation
total_generation = export_df["Generation (kWh)"].sum()
available_generation = total_generation

allocation_results = []

for _, row in import_df.iterrows():
    mpan = row["MPAN"]
    cons = float(row["Consumption (kWh)"])
    gen_rate = float(row["Tariff From Generation (p/kWh)"])
    grid_rate = float(row["Tariff From Grid (p/kWh)"])

    from_gen = min(available_generation, cons)
    from_grid = cons - from_gen
    match_pct = (from_gen / cons) * 100 if cons > 0 else 0

    revenue_gen = from_gen * gen_rate / 100
    revenue_grid = from_grid * grid_rate / 100
    total_cost = revenue_gen + revenue_grid

    allocation_results.append({
        "MPAN": mpan,
        "Total Consumption (kWh)": cons,
        "From Generation (kWh)": from_gen,
        "From Grid (kWh)": from_grid,
        "Match %": round(match_pct, 2),
        "Cost from Generation (£)": revenue_gen,
        "Cost from Grid (£)": revenue_grid,
        "Total Cost (£)": total_cost
    })

    available_generation -= from_gen

# Spill calculation
transferred_to_consumers = total_generation - available_generation
spilled_to_grid = max(available_generation, 0)
private_revenue = transferred_to_consumers * private_rate / 100
uc_revenue = spilled_to_grid * uc_market_rate / 100
total_export_revenue = private_revenue + uc_revenue

export_results = {
    "Total Generation (kWh)": total_generation,
    "Transferred to Consumers (kWh)": transferred_to_consumers,
    "Spilled to Grid (kWh)": spilled_to_grid,
    "% Left Over": round((spilled_to_grid / total_generation) * 100, 2) if total_generation > 0 else 0,
    "Private Market Revenue (£)": round(private_revenue, 2),
    "UC Market Revenue (£)": round(uc_revenue, 2),
    "Total Revenue (£)": round(total_export_revenue, 2)
}

# Display results
st.header("📊 Import MPAN Allocation Results")
st.dataframe(pd.DataFrame(allocation_results), use_container_width=True)

st.header("⚡ Export MPAN Result")
st.dataframe(pd.DataFrame([export_results]), use_container_width=True)

# Bar chart
st.subheader("💰 Consumer Cost Breakdown")
fig, ax = plt.subplots()
plot_df = pd.DataFrame(allocation_results)
ax.bar(plot_df["MPAN"].astype(str), plot_df["Total Cost (£)"], color=PRIMARY_COLOR)
ax.set_ylabel("Total Cost (£)")
ax.set_title("Import MPAN Cost")
st.pyplot(fig)




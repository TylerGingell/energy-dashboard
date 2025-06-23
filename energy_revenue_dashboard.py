import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="UrbanChain Dashboard", layout="wide")
PRIMARY_COLOR = "#00d2c6"
st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>UrbanChain Dashboard -  Gen vs Grid Allocation</h1>", unsafe_allow_html=True)

st.sidebar.header("Rates")
private_rate = st.sidebar.number_input("Private Market Rate (p/kWh)", value=5.0)
uc_market_rate = st.sidebar.number_input("UC Market Rate (p/kWh)", value=8.5)

# Inputs
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

st.subheader("📥 Import MPANs")
import_df = st.data_editor(default_imports, num_rows="dynamic", use_container_width=True)

st.subheader("⚡ Export MPAN")
export_df = st.data_editor(default_export, num_rows="dynamic", use_container_width=True)

# Calculation
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

# Export
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

# Results
st.subheader("📊 Import MPAN Summary")
summary_df = pd.DataFrame(allocation_results)
st.dataframe(summary_df, use_container_width=True)

st.subheader("📦 Export MPAN Summary")
st.dataframe(pd.DataFrame([export_results]), use_container_width=True)

# Charts layout
st.markdown("## 📈 Visual Insights")
col1, col2 = st.columns(2)

# Pie per MPAN
with col1:
    st.markdown("#### 🔍 Consumption Split (Gen vs Grid)")
    for _, row in summary_df.iterrows():
        fig, ax = plt.subplots()
        ax.pie([row["From Gen (kWh)"], row["From Grid (kWh)"]],
               labels=["Gen", "Grid"],
               autopct="%1.1f%%",
               colors=[PRIMARY_COLOR, "#888888"])
        ax.set_title(f"MPAN {row['MPAN']}")
        st.pyplot(fig)

# Stacked bar
with col2:
    st.markdown("#### 💸 Cost Breakdown per MPAN")
    cost_df = summary_df[["MPAN", "Gen Cost (£)", "Grid Cost (£)"]].set_index("MPAN")
    cost_df.plot(kind="bar", stacked=True, color=[PRIMARY_COLOR, "#888888"], figsize=(6,4))
    plt.ylabel("Cost (£)")
    plt.title("Stacked Costs")
    st.pyplot(plt.gcf())

# Export pie
st.markdown("#### ⚡ Export Use Breakdown")
fig3, ax3 = plt.subplots()
ax3.pie([total_transferred, spilled], labels=["To Consumers", "Spilled"],
        autopct="%1.1f%%", colors=[PRIMARY_COLOR, "#888888"])
ax3.set_title("Generation Use")
st.pyplot(fig3)

# Match % Bar Chart
st.markdown("#### 📊 Match % by MPAN")
fig4, ax4 = plt.subplots()
colors = [PRIMARY_COLOR if v >= 85 else '#ff4d4d' for v in summary_df["Match %"]]
ax4.bar(summary_df["MPAN"].astype(str), summary_df["Match %"], color=colors)
ax4.set_ylabel("Match %")
ax4.set_ylim(0, 100)
ax4.set_title("Match % by MPAN")
st.pyplot(fig4)

# Revenue Bar Chart
st.markdown("#### 💰 Export Revenue Breakdown")
fig5, ax5 = plt.subplots()
ax5.bar(["Private Market", "UC Market"], [private_revenue, uc_revenue], color=[PRIMARY_COLOR, "#888888"])
ax5.set_ylabel("Revenue (£)")
ax5.set_title("Export MPAN Revenue Sources")
st.pyplot(fig5)

# Thermometer chart
st.markdown("#### 🌡️ Generation Utilisation Thermometer")
fig6, ax6 = plt.subplots(figsize=(7, 1.2))
ax6.barh(["Generation Usage"], [total_transferred], color=PRIMARY_COLOR, label="Transferred to Consumers")
ax6.barh(["Generation Usage"], [spilled], left=[total_transferred], color="#888888", label="Spilled to Grid")
ax6.set_xlim(0, total_generation)
ax6.set_xlabel("kWh")
ax6.set_title("Total Generation Allocation")
ax6.legend(loc="upper right")
st.pyplot(fig6)




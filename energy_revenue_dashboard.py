import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="UrbanChain Dashboard", layout="wide")
PRIMARY_COLOR = "#00d2c6"

st.markdown(f"<h1 style='color:{PRIMARY_COLOR};'>⚡ UrbanChain Dashboard – Manual Gen vs Grid Allocation</h1>", unsafe_allow_html=True)

st.sidebar.header("Rates")
private_rate = st.sidebar.number_input("Private Market Rate (p/kWh)", value=5.0)
uc_market_rate = st.sidebar.number_input("UC Market Rate (p/kWh)", value=8.5)

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

import_df = st.data_editor(default_imports, num_rows="dynamic", use_container_width=True)
export_df = st.data_editor(default_export, num_rows="dynamic", use_container_width=True)

total_transferred = import_df["From Generation (kWh)"].sum()
total_generation = export_df["Total Generation (kWh)"].sum()
spilled = max(total_generation - total_transferred, 0)

allocation_results = []
for _, row in import_df.iterrows():
    mpan = row["MPAN"]
    cons = row["Total Consumption (kWh)"]
    from_gen = row["From Generation (kWh)"]
    from_grid = row["From Grid (kWh)"]
    gen_rate = row["Tariff From Generation (p/kWh)"]
    grid_rate = row["Tariff From Grid (p/kWh)"]
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
        "Total Cost (£)": total_cost
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

st.markdown("## 🧾 Key Headlines")
left, right = st.columns(2)
with left:
    st.markdown(f"""
    <div style='background-color: #f9f9f9; padding: 1rem; border-radius: 0.5rem;'>
        <h4 style='color:{PRIMARY_COLOR}'>🔢 Summary</h4>
        <p><b>Total Generation:</b> {total_generation:,.0f} kWh</p>
        <p><b>Total Consumption:</b> {summary_df['Consumption (kWh)'].sum():,.0f} kWh</p>
        <p><b>Match %:</b> {summary_df['Match %'].mean():.1f}%</p>
        <p><b>Generation Left Over:</b> {spilled:,.0f} kWh</p>
        <p><b>Total Savings:</b> £{(summary_df['Grid Cost (£)'].sum() - summary_df['Gen Cost (£)'].sum()):,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("#### 🌡️ Generation Utilisation Thermometer")
    fig6, ax6 = plt.subplots(figsize=(6.5, 1.2))
    ax6.barh(["Generation Usage"], [total_transferred], color=PRIMARY_COLOR, label="Transferred to Consumers")
    ax6.barh(["Generation Usage"], [spilled], left=[total_transferred], color="#888888", label="Spilled to Grid")
    ax6.set_xlim(0, total_generation)
    ax6.set_xlabel("kWh")
    ax6.set_title("Total Generation Allocation")
    ax6.legend(loc="upper right")
    st.pyplot(fig6)

st.markdown("## 🔍 MPAN Filter")
mpan_options = ["All"] + sorted(summary_df["MPAN"].astype(str).unique().tolist())
selected_mpan = st.selectbox("Select MPAN to view details", mpan_options)

filtered_df = summary_df if selected_mpan == "All" else summary_df[summary_df["MPAN"].astype(str) == selected_mpan]

st.subheader("📊 Import MPAN Summary")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("📦 Export MPAN Summary")
st.dataframe(export_summary, use_container_width=True)

st.markdown("---")
st.markdown("## 📈 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔍 Consumption Split (Gen vs Grid)")
    for _, row in filtered_df.iterrows():
        gen_val = row["From Gen (kWh)"]
        grid_val = row["From Grid (kWh)"]
        if gen_val + grid_val > 0:
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie([gen_val, grid_val],
                   labels=["Gen", "Grid"],
                   autopct="%1.1f%%",
                   colors=[PRIMARY_COLOR, "#888888"])
            ax.set_title(f"MPAN {row['MPAN']}")
            st.pyplot(fig)
        else:
            st.markdown(f"❗ MPAN {row['MPAN']} has no Gen/Grid split to display.")

with col2:
    st.markdown("#### 💸 Cost Breakdown per MPAN")
    cost_df = summary_df[["MPAN", "Gen Cost (£)", "Grid Cost (£)"]].set_index("MPAN")
    cost_df.plot(kind="bar", stacked=True, color=[PRIMARY_COLOR, "#888888"], figsize=(6, 4))
    plt.ylabel("Cost (£)")
    plt.title("Stacked Costs")
    st.pyplot(plt.gcf())

st.markdown("#### ⚡ Export Use Breakdown")
fig3, ax3 = plt.subplots(figsize=(5, 3))
ax3.pie([total_transferred, spilled], labels=["To Consumers", "Spilled"],
        autopct="%1.1f%%", colors=[PRIMARY_COLOR, "#888888"])
ax3.set_title("Generation Use")
st.pyplot(fig3)

col_match, col_rev = st.columns(2)

with col_match:
    st.markdown("#### 📊 Match % by MPAN")
    fig4, ax4 = plt.subplots(figsize=(5, 3))
    colors = [PRIMARY_COLOR if v >= 85 else '#ff4d4d' for v in summary_df["Match %"]]
    ax4.bar(summary_df["MPAN"].astype(str), summary_df["Match %"], color=colors)
    ax4.set_ylabel("Match %")
    ax4.set_ylim(0, 100)
    ax4.set_title("Match % by MPAN")
    st.pyplot(fig4)

with col_rev:
    st.markdown("#### 💰 Export Revenue Breakdown")
    fig5, ax5 = plt.subplots(figsize=(5, 3))
    ax5.bar(["Private Market", "UC Market"], [private_revenue, uc_revenue], color=[PRIMARY_COLOR, "#888888"])
    ax5.set_ylabel("Revenue (£)")
    ax5.set_title("Export MPAN Revenue Sources")
    st.pyplot(fig5)






import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Branding
PRIMARY_COLOR = "#00d2c6"
st.set_page_config(page_title="UrbanChain MPAN Dashboard", layout="wide")

# Navigation
st.sidebar.title("📁 Navigation")
page = st.sidebar.radio("Go to", ["Upload & Edit Data", "Summary & Charts", "Settings & Help"])

# Sample Data
sample_data = pd.DataFrame({
    "MPAN": ["1234567890123", "1234567890123", "1234567890123"],
    "Month": ["2025-06", "2025-06", "2025-06"],
    "Flow Type": ["Import", "Export", "Generation"],
    "Volume (kWh)": [90000, 5000, 100000],
    "Unit Rate (p/kWh)": [20.0, 8.5, 0],
    "Standing Charge (£/day)": [0.25, 0.0, 0.0],
    "Notes": ["Main site import", "Spill to grid", "Forecasted gen"]
})

# Session state to persist data
if "df" not in st.session_state:
    st.session_state.df = sample_data.copy()

# PAGE 1: Upload & Edit
if page == "Upload & Edit Data":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>📥 Upload or Edit MPAN Flow Data</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            st.session_state.df = pd.read_excel(uploaded_file)

    st.markdown("Edit your MPAN flow data below:")
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

    st.markdown("---")
    st.markdown("⬇️ You can go to **Summary & Charts** to see your results.")

# PAGE 2: Summary & Charts
elif page == "Summary & Charts":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>📊 MPAN Summary & Charts</h2>", unsafe_allow_html=True)
    df = st.session_state.df.copy()

    # Data prep
    df["Volume (kWh)"] = pd.to_numeric(df["Volume (kWh)"], errors="coerce").fillna(0)
    df["Unit Rate (p/kWh)"] = pd.to_numeric(df["Unit Rate (p/kWh)"], errors="coerce").fillna(0)
    df["Standing Charge (£/day)"] = pd.to_numeric(df["Standing Charge (£/day)"], errors="coerce").fillna(0)
    df["Month"] = df["Month"].fillna("All")
    df["Flow Type"] = df["Flow Type"].fillna("Other")

    grouped = df.groupby(["MPAN", "Month"])
    summary = []

    for (mpan, month), group in grouped:
        imports = group[group["Flow Type"] == "Import"]
        exports = group[group["Flow Type"] == "Export"]
        gens = group[group["Flow Type"] == "Generation"]

        import_vol = imports["Volume (kWh)"].sum()
        export_vol = exports["Volume (kWh)"].sum()
        generation = gens["Volume (kWh)"].sum()
        standing = imports["Standing Charge (£/day)"].mean() * 365 if not imports.empty else 0

        rev_import = (imports["Volume (kWh)"] * imports["Unit Rate (p/kWh)"] / 100).sum()
        rev_export = (exports["Volume (kWh)"] * exports["Unit Rate (p/kWh)"] / 100).sum()
        sleeved_vol = max(min(generation, import_vol), 0)
        spill = max(generation - sleeved_vol, 0)
        match_pct = sleeved_vol / generation * 100 if generation else 0

        # Business rule: Match bonus
        bonus_p = 0.5 if match_pct >= 85 else 0.0
        bonus_revenue = sleeved_vol * bonus_p / 100
        total_rev = rev_import + rev_export + bonus_revenue
        net_rev = total_rev - standing

        summary.append({
            "MPAN": mpan,
            "Month": month,
            "Import Volume": import_vol,
            "Export Volume": export_vol,
            "Generation Volume": generation,
            "Match %": round(match_pct, 2),
            "Spill (kWh)": round(spill, 2),
            "Import Revenue (£)": rev_import,
            "Export Revenue (£)": rev_export,
            "Bonus Revenue (£)": round(bonus_revenue, 2),
            "Standing Charges (£)": round(standing, 2),
            "Net Revenue (£)": round(net_rev, 2),
        })

    result_df = pd.DataFrame(summary)
    st.dataframe(result_df, use_container_width=True)

    # Charts
    st.subheader("📉 Net Revenue by MPAN")
    chart_df = result_df.groupby("MPAN")["Net Revenue (£)"].sum().reset_index()
    fig, ax = plt.subplots()
    ax.bar(chart_df["MPAN"].astype(str), chart_df["Net Revenue (£)"], color=PRIMARY_COLOR)
    ax.set_ylabel("Net Revenue (£)")
    st.pyplot(fig)

    # Download
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Summary as CSV", data=csv, file_name="mpan_summary.csv", mime="text/csv")

# PAGE 3: Settings & Help
elif page == "Settings & Help":
    st.markdown(f"<h2 style='color:{PRIMARY_COLOR};'>⚙️ Settings & Help</h2>", unsafe_allow_html=True)
    st.markdown("This app supports:")
    st.markdown("""
    - Multiple MPANs with one or more flow types each
    - Import, Export, and Generation tracking
    - Monthly or aggregated summaries
    - Match % logic with optional bonus
    - Highlighting for low-match or loss sites
    - CSV/Excel upload and download
    """)

    st.markdown("### 📄 Sample File Format")
    st.dataframe(sample_data)

    sample_csv = sample_data.to_csv(index=False).encode("utf-8")
    st.download_button("Download Sample CSV", data=sample_csv, file_name="sample_mpan_data.csv", mime="text/csv")




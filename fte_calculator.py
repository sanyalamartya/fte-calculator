import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FTE Calculator", layout="centered")

st.title("👥 FTE Requirement Calculator (Back-office Ops)")
st.markdown(
    "Calculate **total FTEs** and an **hour-by-hour staffing plan** "
    "based on workload, TAT targets, compliance %, spillover, and staffing parameters."
)

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Parameters")

# Staffing parameters
staffed_time = st.sidebar.number_input(
    "Staffed Time per FTE (minutes)", min_value=60.0, max_value=720.0, value=540.0, step=30.0
)
productive_time = st.sidebar.number_input(
    "Productive Time per FTE (minutes)", min_value=30.0, max_value=720.0, value=408.0, step=30.0
)

# Derived productive minutes per hour
productive_per_hour = productive_time / (staffed_time / 60.0)

# Workload parameters
hours = st.sidebar.number_input("Number of hours to plan for", min_value=1, max_value=24, value=9)

# --- AHT with 2 decimal precision (IMPORTANT FIX) ---
aht = st.sidebar.number_input(
    "Average Handling Time (mins per case)",
    min_value=0.01,
    max_value=999.99,
    value=5.00,
    step=0.01,
    format="%.2f"
)

tat_target = st.sidebar.number_input("TAT Target (minutes)", min_value=15, max_value=480, value=120)
tat_percent = st.sidebar.slider("TAT Compliance Target (%)", min_value=50, max_value=100, value=85, step=5)

# Hourly volume inputs
st.sidebar.markdown("### Enter hourly inflow volume")
volumes = [
    st.number_input(f"Hour {h+1} Volume", min_value=0, value=20 * (h + 1), key=f"vol{h}")
    for h in range(hours)
]

# Spillover input
spillover_volume = st.sidebar.number_input("Spillover Volume (after shift hours)", min_value=0, value=0)

# --- Calculations ---
workloads = [v * aht for v in volumes]  # workload in minutes
fte_per_hour = []

tat_window = max(1, tat_target // 60)  # Convert TAT to hours, minimum 1

for i in range(hours):
    start = max(0, i - tat_window + 1)
    window_load = sum(workloads[start: i + 1])
    avg_load = window_load / tat_window
    ftes = avg_load / productive_per_hour
    fte_per_hour.append(round(ftes, 2))

# Spillover workload
spillover_workload = spillover_volume * aht
spillover_fte = spillover_workload / productive_time

# Total FTE requirement
total_fte = (sum(workloads) + spillover_workload) / productive_time

# --- Results DataFrame ---
df = pd.DataFrame({
    "Hour": [f"{i+1}" for i in range(hours)],
    "Volume": volumes,
    "AHT (mins)": [round(aht, 2)] * hours,
    "Workload (mins)": workloads,
    "FTE Required": fte_per_hour
})

# --- Display ---
st.subheader("📊 Hourly Staffing Plan")
st.dataframe(df)

st.subheader("✅ Total FTEs Needed (Including Spillover)")
st.metric("FTEs Required", f"{total_fte:.2f}")

if spillover_volume > 0:
    st.markdown(
        f"ℹ️ Includes **{spillover_volume} spillover cases** "
        f"= {spillover_fte:.2f} additional FTEs."
    )

st.markdown(
    f"📌 TAT Compliance Target: **{tat_percent}%** of cases within **{tat_target} minutes**."
)

# Chart
st.bar_chart(df.set_index("Hour")["FTE Required"])

# --- Explanation ---
st.markdown("### ℹ️ Why Peak ≠ Total FTEs")
st.write(
    f"Peak hourly requirement may reach **{max(df['FTE Required']):.2f} FTEs**, "
    f"but overall only **{total_fte:.2f} FTEs** are needed because work can be smoothed "
    f"over the **{tat_window}-hour TAT window**. Only **{tat_percent}%** must be cleared "
    "inside the TAT, allowing workload balancing without breaching SLA."
)

# --- Download Staffing Plan ---
st.subheader("📥 Download Staffing Plan")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="fte_staffing_plan.csv",
    mime="text/csv",
)

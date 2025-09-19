import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FTE Calculator", layout="centered")

st.title("👥 FTE Requirement Calculator (Back-office Ops)")
st.markdown(
    "Calculate **total FTEs** and an **hour-by-hour staffing plan** "
    "based on workload, TAT target, compliance %, and spillover."
)

# --- Constants ---
FTE_PRODUCTIVE_MINUTES = 408
SHIFT_MINUTES = 540
PRODUCTIVE_PER_HOUR = FTE_PRODUCTIVE_MINUTES / 9  # ~45.3 mins per hr

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Parameters")

hours = st.sidebar.number_input("Number of hours to plan for", min_value=1, max_value=24, value=9)
aht = st.sidebar.number_input("Average Handling Time (mins per case)", min_value=1, value=5)
tat_target = st.sidebar.number_input("TAT Target (minutes)", min_value=15, max_value=480, value=120)
tat_percent = st.sidebar.slider("TAT Compliance Target (%)", min_value=50, max_value=100, value=85, step=5)

st.sidebar.markdown("### Enter hourly inflow volume")
volumes = [st.number_input(f"Hour {h+1} Volume", min_value=0, value=20*(h+1), key=f"vol{h}") for h in range(hours)]

# Spillover input
spillover_volume = st.sidebar.number_input("Spillover Volume (after shift hours)", min_value=0, value=0)

# --- Calculations ---
workloads = [v * aht for v in volumes]  # workload in minutes
fte_per_hour = []

tat_window = max(1, tat_target // 60)  # Convert TAT to hours, min = 1

for i in range(hours):
    start = max(0, i - tat_window + 1)
    window_load = sum(workloads[start:i+1])
    avg_load = window_load / tat_window
    ftes = avg_load / PRODUCTIVE_PER_HOUR
    fte_per_hour.append(round(ftes, 2))

# Spillover workload
spillover_workload = spillover_volume * aht
spillover_fte = spillover_workload / FTE_PRODUCTIVE_MINUTES

# Total FTE requirement
total_fte = (sum(workloads) + spillover_workload) / FTE_PRODUCTIVE_MINUTES

# --- Results DataFrame ---
df = pd.DataFrame({
    "Hour": [f"{i+1}" for i in range(hours)],
    "Volume": volumes,
    "AHT (mins)": [aht] * hours,
    "Workload (mins)": workloads,
    "FTE Required": fte_per_hour
})

# --- Display ---
st.subheader("📊 Hourly Staffing Plan")
st.dataframe(df)

st.subheader("✅ Total FTEs Needed (Including Spillover)")
st.metric("FTEs Required", f"{total_fte:.1f}")

if spillover_volume > 0:
    st.markdown(
        f"ℹ️ Includes **{spillover_volume} spillover cases** "
        f"= {spillover_fte:.2f} additional FTEs."
    )

st.markdown(
    f"📌 TAT Compliance Target: **{tat_percent}% of cases** to be completed within **{tat_target} minutes**."
)

# Chart
st.bar_chart(df.set_index("Hour")["FTE Required"])

# --- Explanation ---
st.markdown("### ℹ️ Why Peak ≠ Total FTEs")
st.write(
    f"Notice how in some hours (like the busiest peak) the requirement goes as high as "
    f"**{max(df['FTE Required']):.2f} FTEs**. However, the overall FTE requirement is only "
    f"**{total_fte:.1f}**. This is because with a TAT of {tat_target} minutes and a compliance "
    f"target of {tat_percent}%, work does not need to be finished instantly within the same hour. "
    "It can be spread (smoothed) across the allowed TAT window, and as long as the compliance "
    "threshold is met, temporary peaks can be absorbed without breaching SLA."
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

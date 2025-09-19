import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FTE Calculator", layout="centered")

st.title("👥 FTE Requirement Calculator (Back-office Ops)")
st.markdown(
    "Calculate **total FTEs** and an **hour-by-hour staffing plan** "
    "based on workload and Turnaround Time (TAT) targets."
)

# Constants
FTE_PRODUCTIVE_MINUTES = 408
SHIFT_MINUTES = 540
PRODUCTIVE_PER_HOUR = FTE_PRODUCTIVE_MINUTES / 9  # ~45.3 mins per hr

# Inputs
st.sidebar.header("📥 Input Parameters")
hours = st.sidebar.number_input("Number of hours to plan for", min_value=1, max_value=24, value=9)
aht = st.sidebar.number_input("Average Handling Time (mins per case)", min_value=1, value=5)
tat_target = st.sidebar.number_input("TAT Target (minutes)", min_value=15, max_value=480, value=120)

st.sidebar.markdown("### Enter hourly inflow volume")
volumes = [st.number_input(f"Hour {h+1} Volume", min_value=0, value=20*(h+1), key=f"vol{h}") for h in range(hours)]

# --- Calculation ---
workloads = [v * aht for v in*]()


st.sidebar.markdown("### Enter workload per hour")
for h in range(hours):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        vol = st.number_input(f"Hour {h+1} Volume", min_value=0, value=100, key=f"vol{h}")
    with col2:
        aht = st.number_input(f"Hour {h+1} AHT (mins)", min_value=1, value=3, key=f"aht{h}")
    volumes.append(vol)
    ahts.append(aht)

# --- Calculation ---
workloads = [v * a for v, a in zip(volumes, ahts)]  # workload in minutes
fte_per_hour = []

# Convert TAT target into hours (minimum 1 hr)
tat_window = max(1, tat_target // 60)

for i in range(hours):
    start = max(0, i - tat_window + 1)
    window_load = sum(workloads[start:i+1])
    avg_load = window_load / tat_window

    ftes = avg_load / PRODUCTIVE_PER_HOUR
    fte_per_hour.append(round(ftes, 2))

# Results
df = pd.DataFrame({
    "Hour": [f"{i+1}" for i in range(hours)],
    "Volume": volumes,
    "AHT (mins)": ahts,
    "Workload (mins)": workloads,
    "FTE Required": fte_per_hour
})

total_fte = sum(workloads) / FTE_PRODUCTIVE_MINUTES

# --- Display ---
st.subheader("📊 Hourly Staffing Plan")
st.dataframe(df)

st.subheader("✅ Total FTEs Needed")
st.metric("FTEs Required", f"{total_fte:.1f}")

st.bar_chart(df.set_index("Hour")["FTE Required"])

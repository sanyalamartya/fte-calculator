import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="FTE Calculator", layout="centered")

st.title("👥 FTE Requirement Calculator (Back-office Ops)")
st.markdown(
    "Calculate **total FTEs** and an **hour-by-hour staffing plan** "
    "based on workload, TAT target, compliance %, spillover, and staffing parameters."
)

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Parameters")

# Staffing parameters
staffed_time = st.sidebar.number_input(
    "Staffed Time per FTE (minutes)", min_value=60, max_value=720, value=540, step=30
)
productive_time = st.sidebar.number_input(
    "Productive Time per FTE (minutes)", min_value=30, max_value=720, value=408, step=30
)

# Derived productive minutes per hour
productive_per_hour = productive_time / (staffed_time / 60)

# Workload parameters
hours = st.sidebar.number_input("Number of hours to plan for", min_value=1, max_value=24, value=9)
aht = st.sidebar.number_input("Average Handling Time (mins per case)", min_value=1, value=5)
tat_target = st.sidebar.number_input("TAT Target (minutes)", min_value=15, max_value=480, value=120)
tat_percent = st.sidebar.slider("TAT Compliance Target (%)", min_value=50, max_value=100, value=85, step=5)

# Hourly volume inputs
st.sidebar.markdown("### Enter hourly inflow volume")
volumes = [
    st.number_input(f"Hour {h+1} Volume", min_value=0, value=20 * (h + 1), key=f"vol{*

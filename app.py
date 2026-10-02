"""app.py - Smart Dustbin Fill-Time Prediction System (Streamlit dashboard)."""
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from prediction import (calculate_rate, clean_history, format_duration,
                        get_status, hours_to_target)
from sensor_simulator import distance_to_fill_percent, sample_history

LID_OPEN_SECONDS = 3      # lid closes automatically after this delay

st.set_page_config(page_title="Smart Dustbin", page_icon="🗑️", layout="wide")

# ---------- Session state (remembers values between clicks) ----------
if "history" not in st.session_state:
    st.session_state.history = sample_history()
if "lid_open" not in st.session_state:
    st.session_state.lid_open = False
    st.session_state.lid_time = 0.0

# ---------- Sidebar: simulated sensor + settings ----------
st.sidebar.header("⚙️ Sensor Simulation")
mode = st.sidebar.radio("Input mode", ["Fill % slider", "Ultrasonic distance (cm)"])
if mode == "Fill % slider":
    current = st.sidebar.slider("Current fill level (%)", 0, 100, 62)
else:
    bin_h = st.sidebar.number_input("Bin height (cm)", 10.0, 200.0, 50.0)
    dist = st.sidebar.slider("Sensor distance (cm)", 0.0, float(bin_h), 19.0)
    current = round(distance_to_fill_percent(dist, bin_h), 1)
    st.sidebar.caption(f"Converted fill level: {current}%")

threshold = st.sidebar.slider("Alert threshold (%)", 50, 100, 80)
show_buzzer = st.sidebar.checkbox("Simulate buzzer / LED", value=True)

if st.sidebar.button("➕ Log current reading to history"):
    new_row = pd.DataFrame({"Time": [datetime.now()], "Fill %": [current]})
    st.session_state.history = pd.concat(
        [st.session_state.history, new_row], ignore_index=True)

# ---------- Calculations ----------
history = clean_history(st.session_state.history)
rate = calculate_rate(history)
h80 = hours_to_target(current, 80, rate)
h100 = hours_to_target(current, 100, rate)
status, icon = get_status(current)

# ---------- Header ----------
st.title("🗑️ Smart Dustbin Fill-Time Prediction System")
st.caption("Monitor the bin, predict when it will be full, and alert before it overflows.")

# ---------- Row 1: main metric cards ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Fill Level", f"{current}%")
c2.metric("Dustbin Status", f"{icon} {status}")
c3.metric("Accumulation Rate",
          f"{rate:.2f} %/hour" if rate is not None else "N/A")
c4.metric("Threshold", f"{threshold}%")
st.progress(int(min(max(current, 0), 100)), text=f"Fill level: {current}%")

# ---------- Row 2: predictions ----------
st.subheader("⏱️ Prediction")
if rate is None:
    st.info("Not enough data for prediction.")
elif rate <= 0:
    st.info("Waste level is not increasing, so no prediction is possible.")
p1, p2 = st.columns(2)
p1.metric("Time to reach 80%", format_duration(h80))
p2.metric("Time to reach 100% (full)", format_duration(h100))

# ---------- Row 3: overflow alert + lid ----------
a_col, l_col = st.columns(2)

with a_col:
    st.subheader("🚨 Overflow Alert")
    if current >= threshold:
        st.error("⚠️ **OVERFLOW WARNING – Dustbin needs attention.**")
        if show_buzzer:
            st.markdown("### 🔴 LED: ON  &nbsp; 🔔 Buzzer: BEEP BEEP!")
    else:
        st.success("✅ Everything is normal.")
        if show_buzzer:
            st.markdown("### 🟢 LED: OFF  &nbsp; 🔕 Buzzer: silent")


def _open_lid():
    st.session_state.lid_open = True
    st.session_state.lid_time = time.time()


def _close_lid():
    st.session_state.lid_open = False


@st.fragment(run_every="1s")          # refreshes only this box every second
def lid_panel():
    # Auto-close after a short delay (simulates the servo returning)
    if st.session_state.lid_open and \
            time.time() - st.session_state.lid_time >= LID_OPEN_SECONDS:
        _close_lid()
    st.subheader("🤖 Automatic Lid (PIR + Servo)")
    b1, b2 = st.columns(2)
    b1.button("🧍 User Detected", on_click=_open_lid)
    b2.button("Close lid now", on_click=_close_lid)
    if st.session_state.lid_open:
        st.warning("User detected")
        st.metric("Lid Status", "🔓 OPEN")
    else:
        st.metric("Lid Status", "🔒 CLOSED")


with l_col:
    lid_panel()

# ---------- Row 4: history ----------
st.subheader("📈 Fill-Level History")
st.caption("Edit, add or delete rows in the table. The prediction updates automatically.")
edited = st.data_editor(
    st.session_state.history,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Time": st.column_config.DatetimeColumn("Date/Time", format="DD MMM YYYY, hh:mm A"),
        "Fill %": st.column_config.NumberColumn("Fill %", min_value=0, max_value=100),
    },
)
st.session_state.history = edited

if len(history) >= 1:
    fig = px.line(history, x="Time", y="Fill %", markers=True,
                  title="Dustbin fill level over time", range_y=[0, 105])
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Threshold {threshold}%")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No valid readings yet. Add some rows to the table above.")

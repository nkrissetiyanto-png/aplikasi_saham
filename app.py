import streamlit as st
import plotly.graph_objects as go
from prediksi_engine import reconstruct_intraday, train_models, predict_next_15m
from data_loader import load_data
from strategy import get_signal
from notifier import send_alert
import time

# SET PAGE CONFIG → HARUS PALING AWAL
st.set_page_config(page_title="Nanang AI Trading", layout="wide")

# Auto-refresh setiap 15 menit
st.write("Auto refresh aktif setiap 15 menit...")
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

if time.time() - st.session_state["last_refresh"] > 900:
    st.session_state["last_refresh"] = time.time()
    st.experimental_rerun()

# Dark mode styling
st.markdown(
    """<style>
    body {background-color: #0e1117; color: #e0e0e0;}
    </style>""",
    unsafe_allow_html=True
)

st.title("🚀 Nanang AI — Prediksi Saham 15 Menit (Dark Mode)")

# Load data & model
data = load_data()
intraday = reconstruct_intraday(data)
model = train_models(intraday)
prob, sm = predict_next_15m(model, intraday)

signal = get_signal(prob, sm)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Probabilitas Naik", f"{prob*100:.2f}%")
col2.metric("Smart Money Score", sm)
col3.metric("Signal", signal)

# Chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=intraday["Datetime"],
    y=intraday["Price"],
    mode="lines",
    name="Price",
    line=dict(color="#00c3ff")
))
fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

# Telegram alerts
if signal in ["BUY", "SELL"]:
    send_alert(f"🔔 SIGNAL {signal} — Prob naik: {prob*100:.2f}% | SM: {sm}")
    st.success("📨 Alert dikirim ke Telegram!")

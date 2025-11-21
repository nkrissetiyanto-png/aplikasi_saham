import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from data_loader import load_data
from prediksi_engine import reconstruct_intraday, train_models, predict_next_15m
from strategy import get_signal
from notifier import send_alert

st.set_page_config(page_title="Nanang AI Trading", layout="wide")

st.markdown(
    """<style>
    body {background-color: #0e1117; color: #e0e0e0;}
    </style>""", unsafe_allow_html=True)

st.title("🚀 Nanang AI — Prediksi Saham 15 Menit (Dark Mode)")

st_autorefresh(interval=900000, key="refresh")

data = load_data()
intraday = reconstruct_intraday(data)
xgb = train_models(intraday)
prob, sm = predict_next_15m(xgb, intraday)

signal = get_signal(prob, sm)

col1, col2, col3 = st.columns(3)
col1.metric("Probabilitas Naik", f"{prob*100:.2f}%")
col2.metric("Smart Money Score", sm)
col3.metric("Signal", signal)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=intraday["Datetime"], y=intraday["Price"],
    mode="lines", name="Price", line=dict(color="#00c3ff")
))
fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

if signal in ["BUY","SELL"]:
    send_alert(f"🔔 SIGNAL {signal} — Prob naik: {prob*100:.2f}% | SM: {sm}")
    st.success("📨 Alert dikirim ke Telegram!")

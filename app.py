import streamlit as st
import plotly.graph_objects as go
from prediksi_engine import reconstruct_intraday, train_models, predict_next_15m
from data_loader import load_data
from strategy import get_signal
from notifier import send_alert
import time

# PAGE CONFIG WAJIB PALING ATAS
st.set_page_config(page_title="Nanang AI Trading", layout="wide")

# Auto-refresh
st.write("Auto refresh aktif setiap 15 menit...")
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

if time.time() - st.session_state["last_refresh"] > 900:
    st.session_state["last_refresh"] = time.time()
    st.experimental_rerun()

# Dark mode style
st.markdown(
    """<style>
        body {background-color: #0e1117; color: #e0e0e0;}
    </style>""",
    unsafe_allow_html=True
)

st.title("🚀 Nanang AI — Prediksi Saham 15 Menit (Dark Mode)")

# PILIH SAHAM
# ticker = st.selectbox("Pilih Saham", ["BBNI.JK", "BRIS.JK"])
ticker = st.selectbox("Pilih Aset", [
    "BBNI.JK", "BRIS.JK",
    "BTC-USD", "ETH-USD", "SOL-USD",
    "EURUSD=X", "USDJPY=X", "XAUUSD=X",
    "CL=F", "GC=F", "ES=F", "NQ=F"
])

# LOAD DATA
data = load_data(ticker)

# CEK DATA VALID
required_cols = ["Open","High","Low","Close","Volume"]
if not all(col in data.columns for col in required_cols):
    st.error("❌ Data dari Yahoo Finance tidak valid. Kolom OHLCV tidak ditemukan.")
    st.stop()

# JANGAN DROP LAGI (sudah bersih)
# data = data.dropna(subset=required_cols)

# RECONSTRUCT DATA
intraday = reconstruct_intraday(data)
model = train_models(intraday)
prob, sm = predict_next_15m(model, intraday)

signal = get_signal(prob, sm)

col1, col2, col3 = st.columns(3)
col1.metric("Probabilitas Naik", f"{prob*100:.2f}%")
col2.metric("Smart Money Score", sm)
col3.metric("Signal", signal)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=intraday["Datetime"],
    y=intraday["Price"],
    mode="lines",
    line=dict(color="#00c3ff"),
    name="Price"
))
fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

if signal in ["BUY", "SELL"]:
    send_alert(f"🔔 SIGNAL {signal} — Probabilitas naik: {prob*100:.2f}% | SM={sm}")
    st.success("📨 Alert dikirim!")

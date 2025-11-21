import streamlit as st
import plotly.graph_objects as go
import time
from data_loader import load_yahoo_data, load_toko_data
from prediksi_engine import reconstruct_intraday, train_models, predict_next_15m
from strategy import get_signal
from notifier import send_alert


# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Nanang AI Trading", layout="wide")

st.markdown(
    """
    <style>
        body {background-color: #0e1117; color: #e0e0e0;}
    </style>
    """,
    unsafe_allow_html=True
)

st.write("Auto refresh aktif setiap 15 menit...")
st.experimental_set_query_params(ts=int(time.time()))


# =============================
# TITLE
# =============================
st.title("🚀 Nanang AI — Prediksi Saham 15 Menit (Dark Mode)")

# =============================
# DROPDOWN 1 — PILIH SUMBER DATA
# =============================
source = st.selectbox("Sumber Data", ["Yahoo Finance", "Tokocrypto"])
# ==== AUTO REFRESH KHUSUS TOKOCRYPTO ====
if source == "Tokocrypto":
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="tokocrypto_1m_refresh")

# =============================
# DROPDOWN 2 — PILIH ASET SESUAI SUMBER
# =============================
if source == "Yahoo Finance":
    ticker = st.selectbox("Pilih Saham / Crypto (Yahoo)", [
        "BBNI.JK", "BRIS.JK",
        "BTC-USD", "ETH-USD", "SOL-USD"
    ])
else:
    ticker = st.selectbox("Pilih Crypto (Tokocrypto)", [
        "BTC_USDT", "ETH_USDT", "SOL_USDT"
    ])

if source == "Tokocrypto":
    st_autorefresh = st.experimental_rerun
    st_autorefresh()

# =============================
# LOAD DATA
# =============================
if source == "Yahoo Finance":
    raw = load_yahoo_data(ticker)
else:
    raw = load_toko_data(ticker)

if raw is None or raw.empty:
    st.error("❌ Data kosong atau gagal dimuat.")
    st.stop()


# =============================
# RECONSTRUCT INTRADAY
# =============================
intraday = reconstruct_intraday(raw)

# TRAIN MODEL
model = train_models(intraday)

# PREDICT
prob, sm = predict_next_15m(model, intraday)
signal = get_signal(prob, sm)


# =============================
# METRICS
# =============================
col1, col2, col3 = st.columns(3)
col1.metric("Probabilitas Naik", f"{prob*100:.2f}%")
col2.metric("Smart Money Score", sm)
col3.metric("Signal", signal)


# =============================
# CHART
# =============================
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


# =============================
# NOTIFY (BUY / SELL)
# =============================
if signal in ["BUY", "SELL"]:
    send_alert(f"🔔 SIGNAL {signal} — Prob naik: {prob*100:.2f}% | SM: {sm}")
    st.success("📨 Alert dikirim ke Telegram!")

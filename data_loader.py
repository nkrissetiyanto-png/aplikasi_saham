import yfinance as yf
import pandas as pd
import requests

def load_data(ticker, source="Yahoo Finance", period="1y"):
    if source == "Yahoo Finance":
        return load_yfinance(ticker, period)
    else:
        return load_tokocrypto(ticker)

# ====== 1. YAHOO FINANCE ======
def load_yfinance(ticker, period="1y"):
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=False)

    if df.empty:
        raise ValueError(f"❌ Data kosong dari Yahoo Finance untuk {ticker}")

    df = df.dropna()
    df.reset_index(inplace=True)   # pastikan ada kolom 'Date'
    return df


# ====== 2. TOKOCRYPTO API (24 Jam) ======
def load_tokocrypto(pair="BTC_USDT", interval="15m", limit=200):
    url = "https://api.tokocrypto.com/open/v1/klines"
    params = {
        "symbol": pair,
        "interval": interval,
        "limit": limit
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    if "data" not in data:
        raise ValueError("❌ API Tokocrypto tidak mengembalikan data.")

    df = pd.DataFrame(data["data"])
    if df.empty:
        raise ValueError(f"❌ Data Tokocrypto kosong untuk {pair}")

    # Tokocrypto mengembalikan: [open, high, low, close, volume, closeTime]
    df.columns = ["Open", "High", "Low", "Close", "Volume", "CloseTime"]
    df["Date"] = pd.to_datetime(df["CloseTime"], unit="ms")

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.dropna()

    return df

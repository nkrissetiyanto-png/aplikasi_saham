import yfinance as yf
import pandas as pd
import requests


# =============================
# LOAD DATA YAHOO FINANCE
# =============================
def load_yahoo_data(ticker, period="1y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=False)
        if df is None or df.empty:
            return None

        df = df.dropna()
        df = df[["Open", "High", "Low", "Close", "Volume"]]   # kolom wajib
        return df

    except Exception as e:
        print("Error load_yahoo_data:", e)
        return None


# =============================
# LOAD DATA TOKOCRYPTO (PUBLIC API)
# =============================
def load_toko_data(symbol, interval="1d", limit=365):
    url = "https://api.tokocrypto.com/open/v1/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print("HTTP gagal:", r.text)
            return None

        data = r.json().get("data", None)
        if not data:
            return None

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])

        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)

        df.index = pd.date_range(end=pd.Timestamp.utcnow(), periods=len(df), freq="D")

        return df

    except Exception as e:
        print("Error load_toko_data:", e)
        return None

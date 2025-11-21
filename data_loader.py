import yfinance as yf
import pandas as pd

def load_data(ticker="BBNI.JK", period="1y"):
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=False)

    if df.empty:
        raise ValueError(f"❌ Data kosong untuk {ticker}")

    df = df.dropna()

    # pastikan kolom Datetime ada
    df.reset_index(inplace=True)

    return df

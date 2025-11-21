import yfinance as yf
import pandas as pd

def load_data(tickers=["BBNI.JK", "BRIS.JK"], period="1y"):
    df_list = []
    for t in tickers:
        df = yf.download(t, period=period, interval="1d", auto_adjust=False)
        if df.empty:
            print(f"⚠️ Data kosong untuk {t}, dilewati.")
            continue
        df.dropna(inplace=True)
        df["Ticker"] = t
        df_list.append(df)
    if not df_list:
        raise ValueError("❌ Tidak ada data yang berhasil diambil!")
    return pd.concat(df_list)

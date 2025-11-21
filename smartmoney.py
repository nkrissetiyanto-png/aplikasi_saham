import numpy as np
import pandas as pd

def smart_money_features(df):
    df = df.copy()
    df["Return"] = df["Price"].pct_change()
    df["VWAP"] = (df["Price"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    df["VWAP_dev"] = (df["Price"] - df["VWAP"]) / df["VWAP"]
    df["CVD"] = np.where(df["Return"] > 0, df["Volume"], -df["Volume"]).cumsum()
    df["VolImb"] = df["Volume"] * np.sign(df["Return"])
    df["SM_Score"] = (
        (df["VWAP_dev"] > 0).astype(int) +
        (df["CVD"].diff() > 0).astype(int) +
        (df["VolImb"] > 0).astype(int)
    )
    df["SM_Label"] = df["SM_Score"].apply(
        lambda x: "Strong Accumulation" if x >= 2 else
                  "Accumulation" if x == 1 else
                  "Neutral" if x == 0 else
                  "Distribution"
    )
    return df

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from smartmoney import smart_money_features

def reconstruct_intraday(df, intervals=15):
    df = df.copy()
    out = []

    # pastikan kolom datetime benar
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    for _, row in df.iterrows():

        idx = row["Date"]     # <-- FIX TERPENTING

        O, H, L, C, V = row["Open"], row["High"], row["Low"], row["Close"], row["Volume"]

        # validasi data
        if any(pd.isna([O, H, L, C, V])):
            continue

        try:
            O, H, L, C, V = float(O), float(H), float(L), float(C), float(V)
        except:
            continue

        if V == 0 or (H - L) == 0:
            continue

        prices = np.linspace(O, C, intervals) + np.random.normal(0, (H-L)/25, intervals)
        vols = np.abs(np.random.normal(V/intervals, V/(intervals*4), intervals))

        temp = pd.DataFrame({
            "Datetime": [idx + pd.Timedelta(minutes=15*i) for i in range(intervals)],
            "Price": prices,
            "Volume": vols
        })

        out.append(temp)

    if not out:
        return pd.DataFrame(columns=["Datetime","Price","Volume"])

    full = pd.concat(out)
    full.reset_index(drop=True, inplace=True)
    return full

def train_models(intraday):
    intraday = smart_money_features(intraday)
    intraday["Target"] = (intraday["Price"].shift(-1) > intraday["Price"]).astype(int)

    X = intraday[["Price","Volume","Return","VWAP_dev","CVD","VolImb","SM_Score"]].dropna()
    y = intraday["Target"].loc[X.index]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.15)

    model = LGBMClassifier(
        n_estimators=150,
        max_depth=-1,
        learning_rate=0.05
    )
    model.fit(X_tr, y_tr)

    return model


def predict_next_15m(model, intraday):
    last = smart_money_features(intraday).tail(1)
    X_last = last[["Price","Volume","Return","VWAP_dev","CVD","VolImb","SM_Score"]].values
    prob = model.predict_proba(X_last)[0][1]
    return prob, last["SM_Score"].values[0]

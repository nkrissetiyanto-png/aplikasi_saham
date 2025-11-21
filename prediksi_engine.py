import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from smartmoney import smart_money_features

# Rekonstruksi intraday simulasi
def reconstruct_intraday(df, intervals=15):
    df = df.copy()
    reconstructed = []

    for idx, row in df.iterrows():
        O, H, L, C, V = row["Open"], row["High"], row["Low"], row["Close"], row["Volume"]

        if V == 0 or (H - L) == 0:
            continue

        prices = np.linspace(O, C, intervals)
        noise = np.random.normal(0, (H - L) / 25, intervals)
        prices = prices + noise
        
        vol_dist = np.abs(np.random.normal(V/intervals, V/(intervals*4), intervals))

        temp = pd.DataFrame({
            "Datetime": [idx + pd.Timedelta(minutes=15*i) for i in range(intervals)],
            "Price": prices,
            "Volume": vol_dist
        })

        reconstructed.append(temp)

    full = pd.concat(reconstructed)
    full.reset_index(drop=True, inplace=True)
    return full


def train_models(intraday):
    intraday = smart_money_features(intraday)

    intraday["Target"] = (intraday["Price"].shift(-1) > intraday["Price"]).astype(int)

    X = intraday[["Price","Volume","Return","VWAP_dev","CVD","VolImb","SM_Score"]].dropna()
    y = intraday["Target"].loc[X.index]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)

    # MODEL XGBOOST SAJA (karena TensorFlow tidak bisa di Streamlit Cloud)
    xgb = XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.05)
    xgb.fit(X_train, y_train)

    return xgb


def predict_next_15m(xgb, intraday):
    last = smart_money_features(intraday).tail(1)

    X_last = last[["Price","Volume","Return","VWAP_dev","CVD","VolImb","SM_Score"]].values
    prob_xgb = xgb.predict_proba(X_last)[0][1]

    return prob_xgb, last["SM_Score"].values[0]

import os
import requests
import yfinance as yf

# ==========================
# Discord
# ==========================
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# ==========================
# データ取得
# ==========================
def download_data(ticker, interval):

    df = yf.download(
        ticker,
        period="60d",
        interval=interval,
        progress=False,
        auto_adjust=False,
    )

    # MultiIndex対策
    if df.columns.nlevels > 1:
        df.columns = df.columns.get_level_values(0)

    return df


# ==========================
# 移動平均
# ==========================

def calculate_indicators(df):

    df["SMA25"] = df["Close"].rolling(25).mean()
    df["SMA75"] = df["Close"].rolling(75).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    std = df["Close"].rolling(25).std()

    df["Upper1"] = df["SMA25"] + std
    df["Upper2"] = df["SMA25"] + std*2
    df["Upper3"] = df["SMA25"] + std*3

    df["Lower1"] = df["SMA25"] - std
    df["Lower2"] = df["SMA25"] - std*2
    df["Lower3"] = df["SMA25"] - std*3

    df["BB_Width"] = (
        (df["Upper3"] - df["Lower3"])
        / df["SMA25"]
        * 100
    )

    return df



def check_signal(df):

    # 最新3本
    prev2 = df.iloc[-3]
    prev1 = df.iloc[-2]
    curr  = df.iloc[-1]

    # ---------- 前々足 ----------
    prev2_under = prev2["Close"] < prev2["Lower1"]

    prev2_near2 = (
        abs(prev2["Close"] - prev2["Lower2"])
        <
        abs(prev2["Close"] - prev2["Lower1"])
    )

    # ---------- 前足 ----------
    prev1_under = prev1["Close"] < prev1["Lower1"]

    prev1_near2 = (
        abs(prev1["Close"] - prev1["Lower2"])
        <
        abs(prev1["Close"] - prev1["Lower1"])
    )

    # ---------- 現在足 ----------
    curr_under = curr["Close"] < curr["Lower1"]

    curr_near1 = (
        abs(curr["Close"] - curr["Lower1"])
        <
        abs(curr["Close"] - curr["Lower2"])
    )

    return (
        prev2_under
        and prev2_near2
        and prev1_under
        and prev1_near2
        and curr_under
        and curr_near1
    )



def send_discord(df, pair_name, timeframe):

    # 最新足
    last = df.iloc[-1]

    price = float(last["Close"])

    sma25 = float(last["SMA25"])
    sma75 = float(last["SMA75"])
    sma200 = float(last["SMA200"])

    lower1 = float(last["Lower1"])
    lower2 = float(last["Lower2"])

    bb_width = float(last["BB_Width"])

    # ==========================
    # SMA配列
    # ==========================
    values = {
        "M": sma25,
        "L": sma75,
        "Ex": sma200,
    }

    sorted_keys = [
        key for key, _ in sorted(values.items(), key=lambda x: x[1])
    ]

    # 例：MLEx
    pattern = "".join(sorted_keys)

    # 例：M < L < Ex
    order = " < ".join(sorted_keys)

    # ==========================
    # Discord通知
    # ==========================
    message = f"""
🚨 {pair_name}【{timeframe}】

{pattern}｜BBW {bb_width:.3f}

価格      : {price:.3f}

SMA順序   : {order}

25SMA     : {sma25:.3f}
75SMA     : {sma75:.3f}
200SMA    : {sma200:.3f}

-1σ       : {lower1:.3f}
-2σ       : {lower2:.3f}
"""

    requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )


def main():


    WATCHLIST = {
        "USDJPY": "JPY=X",
        "EURUSD": "EURUSD=X",
        "EURGBP": "EURGBP=X",
        "AUDJPY": "AUDJPY=X",
    }

    for pair_name, ticker in WATCHLIST.items():

        print(f"{pair_name} チェック中...")
    
        df = download_data(
            ticker=ticker,
            interval="15m"
        )
    
        df = calculate_indicators(df)
    
        if check_signal(df):
    
            send_discord(
                df=df,
                pair_name=pair_name,
                timeframe="15分"
            )
            
        else:
            print(f"{pair_name}：シグナルなし")



if __name__ == "__main__":
    main()

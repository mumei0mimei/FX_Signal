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
df = yf.download(
    "JPY=X",
    period="10d",
    interval="15m",
    progress=False,
    auto_adjust=False,
)

# MultiIndex対策
if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
    df.columns = df.columns.get_level_values(0)

# ==========================
# 移動平均
# ==========================

df["SMA25"] = df["Close"].rolling(25).mean()
df["SMA75"] = df["Close"].rolling(75).mean()
df["SMA200"] = df["Close"].rolling(200).mean()


# 最新足
last = df.iloc[-1]

price = float(last["Close"])

sma25 = float(last["SMA25"])
sma75 = float(last["SMA75"])
sma200 = float(last["SMA200"])

values = {
    "25SMA": sma25,
    "75SMA": sma75,
    "200SMA": sma200,
}

order = " < ".join(
    key for key, _ in sorted(values.items(), key=lambda x: x[1])
)

print(df.columns)

price = float(last["Close"])

message = f"""
📈 USDJPY【15分足】

価格
{price:.3f}

SMA順序
{order}

25SMA : {sma25:.3f}
75SMA : {sma75:.3f}
200SMA : {sma200:.3f}

取得本数
{len(df)}
"""

requests.post(
    WEBHOOK_URL,
    json={"content": message}
)

print(df.tail())

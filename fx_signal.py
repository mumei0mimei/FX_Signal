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

# 最新足
last = df.iloc[-1]

price = float(last["Close"])

message = f"""
✅ USDJPY取得成功

現在価格
{price:.3f}

取得本数
{len(df)}
"""

requests.post(
    WEBHOOK_URL,
    json={"content": message}
)

print(df.tail())

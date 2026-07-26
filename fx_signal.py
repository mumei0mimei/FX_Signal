import os
import requests
from datetime import datetime

# GitHub SecretsからWebhook URLを取得
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# 現在時刻
now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

message = f"""
✅ GitHub Actions テスト成功！

時刻
{now}

ここまで届けば
・GitHub Actions
・Python
・Discord
の接続は成功です！
"""

response = requests.post(
    WEBHOOK_URL,
    json={"content": message}
)

print("Status:", response.status_code)
print(response.text)

#!/usr/bin/env python3
# test_updated_webhook.py - 更新されたWebhook URLをテスト

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

print("🔍 更新されたWebhook URL テスト")
print("=" * 50)

# 環境変数の確認
n8n_url = os.getenv('N8N_WEBHOOK_URL')
print(f"現在のN8N_WEBHOOK_URL: {n8n_url}")

# テストペイロード
test_payload = {
    "recipient_email": "katsura@hbm-web.co.jp",
    "recipient_name": "田中さん",
    "email_subject": "【テスト】更新されたWebhook URLテスト",
    "email_content": f"""田中様

お世話になっております。

Webhook URL更新後のテストメールです。

【テスト詳細】
- 実行時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')}
- Webhook URL: {n8n_url}
- テスト種別: 環境変数更新後テスト

このメールが届けばWebhook設定が正常です。

どうぞよろしくお願いいたします。""",
    "urgency": "high"
}

print(f"\n📤 テストメール送信中...")
print(f"URL: {n8n_url}")
print(f"宛先: {test_payload['recipient_name']} ({test_payload['recipient_email']})")
print(f"件名: {test_payload['email_subject']}")

try:
    response = requests.post(
        n8n_url,
        json=test_payload,
        timeout=30,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'HannanBusinessMachine-AI-Test/1.0'
        }
    )
    
    print(f"\n📨 結果:")
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンステキスト: '{response.text}'")
    print(f"レスポンス長: {len(response.text)}文字")
    
    if response.headers:
        print(f"\nレスポンスヘッダー:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    
    if response.status_code == 200:
        print(f"\n✅ Webhook呼び出し成功！")
        if response.text:
            try:
                result = response.json()
                print(f"JSONレスポンス: {result}")
            except:
                print(f"テキストレスポンス: {response.text}")
        else:
            print("⚠️ レスポンスボディが空です")
    else:
        print(f"\n❌ エラー: HTTP {response.status_code}")
        print(f"エラー内容: {response.text}")

except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 接続エラー: {e}")
except requests.exceptions.Timeout as e:
    print(f"\n⏰ タイムアウト: {e}")
except Exception as e:
    print(f"\n❌ 予期しないエラー: {e}")

print(f"\n🔗 次の確認項目:")
print(f"1. n8nダッシュボード (https://n8n.xvps.jp) でワークフロー実行履歴を確認")
print(f"2. ワークフローがアクティブ（有効）になっているか確認")
print(f"3. AIサーバーを再起動してLINEからテスト")
print(f"4. Gmail等でメール受信を確認")
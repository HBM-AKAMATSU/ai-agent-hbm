#!/usr/bin/env python3
# test_email_config.py - 環境変数とメール送信設定をテスト

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .envファイルを読み込む
load_dotenv()

print("🔍 メール送信設定診断ツール")
print("=" * 50)

# 1. 環境変数の確認
print("\n1. 環境変数の確認:")
n8n_url = os.getenv('N8N_WEBHOOK_URL')
print(f"   N8N_WEBHOOK_URL: {n8n_url}")
print(f"   値の長さ: {len(n8n_url) if n8n_url else 0}文字")
print(f"   空文字列チェック: {n8n_url == ''}")
print(f"   Noneチェック: {n8n_url is None}")

# 2. Configクラスの確認
print("\n2. Configクラスの確認:")
try:
    from src.config import Config
    print(f"   Config.N8N_WEBHOOK_URL: {Config.N8N_WEBHOOK_URL}")
    print(f"   型: {type(Config.N8N_WEBHOOK_URL)}")
except Exception as e:
    print(f"   ❌ Configクラスの読み込みエラー: {e}")

# 3. EmailSendServiceの初期化確認
print("\n3. EmailSendServiceの初期化:")
try:
    from src.services.email_send_service import EmailSendService
    email_service = EmailSendService()
    print(f"   email_service.n8n_webhook_url: {email_service.n8n_webhook_url}")
    
    # URLチェックロジックの確認
    url = email_service.n8n_webhook_url
    print(f"\n4. URLチェックロジック:")
    print(f"   not url: {not url}")
    print(f"   url == 'disabled': {url == 'disabled'}")
    print(f"   'your-n8n-instance' in url: {'your-n8n-instance' in url}")
    
    should_preview = not url or url == "disabled" or "your-n8n-instance" in url
    print(f"   プレビューモードになる?: {should_preview}")
    
except Exception as e:
    print(f"   ❌ EmailSendServiceの初期化エラー: {e}")
    import traceback
    traceback.print_exc()

# 4. 実際のメール送信テスト
print("\n5. メール送信テスト:")
try:
    if n8n_url and n8n_url != 'disabled' and 'your-n8n-instance' not in n8n_url:
        test_payload = {
            "recipient_email": "test@example.com",
            "recipient_name": "テスト",
            "email_subject": "設定テスト",
            "email_content": f"設定テスト実行時刻: {datetime.now()}",
            "urgency": "normal"
        }
        
        print(f"   テストペイロードでN8Nに送信中...")
        response = requests.post(
            n8n_url,
            json=test_payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   ✅ ステータスコード: {response.status_code}")
        print(f"   レスポンス: {response.text[:100] if response.text else '(空)'}")
    else:
        print("   ⚠️ N8N URLが設定されていないか無効なためスキップ")
except Exception as e:
    print(f"   ❌ メール送信テストエラー: {e}")

print("\n診断完了！")
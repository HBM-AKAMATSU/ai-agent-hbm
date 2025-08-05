#!/usr/bin/env python3
"""
N8N直接テスト - メール送信エラーの切り分け
"""
import requests
import json
from datetime import datetime

def test_n8n_webhook():
    """N8N Webhookに直接リクエストを送信してテスト"""
    
    # N8N Webhook URL
    webhook_url = "https://n8n.xvps.jp/webhook/hannan-email-webhook"
    
    # テストペイロード
    test_payload = {
        "recipient_email": "katsura@hbm-web.co.jp",
        "recipient_name": "田中さん",
        "email_subject": "【テスト】パスワードリセット依頼",
        "email_content": "これはテストメールです。N8Nワークフローの動作確認のため送信しています。",
        "urgency": "high"
    }
    
    print("🔧 N8N Webhook テスト開始")
    print(f"📍 URL: {webhook_url}")
    print(f"📋 ペイロード:")
    print(json.dumps(test_payload, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"✅ ステータスコード: {response.status_code}")
        print(f"📤 レスポンスヘッダー: {dict(response.headers)}")
        
        if response.text:
            print(f"📝 レスポンス内容:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
            except:
                print(response.text)
        else:
            print("📝 レスポンス内容: (空)")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 接続エラー: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"⏰ タイムアウト: {e}")
        return False
    except Exception as e:
        print(f"💥 予期しないエラー: {e}")
        return False

def test_email_send_service():
    """EmailSendServiceのメソッドをテスト"""
    import sys
    import os
    sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')
    
    from services.email_send_service import EmailSendService
    
    email_service = EmailSendService()
    
    print("\n🔧 EmailSendService テスト開始")
    
    # 1. should_send_emailテスト
    test_message = "田中さんにメールお願いします"
    test_response = "ワークフローを実行しました"
    
    should_send = email_service.should_send_email(test_message, test_response)
    print(f"📊 should_send_email: {should_send}")
    
    # 2. extract_email_requestテスト
    email_request = email_service.extract_email_request(test_message, test_response)
    print(f"📊 email_request:")
    print(json.dumps(email_request, indent=2, ensure_ascii=False))
    
    # 3. 実際のN8N送信テスト
    if email_request["should_send"]:
        print(f"\n📤 N8N送信テスト実行中...")
        result = email_service.send_email_via_n8n(email_request)
        print(f"📤 送信結果: {result}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 N8N メール送信システム - デバッグテスト")
    print("=" * 60)
    
    # 1. N8N Webhook 直接テスト
    n8n_success = test_n8n_webhook()
    
    # 2. EmailSendService テスト
    test_email_send_service()
    
    print("\n" + "=" * 60)
    print(f"📊 テスト結果:")
    print(f"   N8N Webhook: {'✅ 成功' if n8n_success else '❌ 失敗'}")
    print("=" * 60)

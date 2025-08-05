#!/usr/bin/env python3
# simple_n8n_test.py - シンプルなn8nテスト

import requests
import json
from datetime import datetime

def test_n8n_webhook():
    """n8n webhookの簡単なテスト"""
    url = "https://n8n.xvps.jp/webhook/hannan-email-webhook"
    
    # テストペイロード
    test_payload = {
        "recipient_email": "akamatsu.d@hbm-web.co.jp",
        "recipient_name": "田中さん",
        "email_subject": "【テスト】メール送信テスト",
        "email_content": "これはn8nメール送信のテストです。",
        "urgency": "normal",
        "test": True,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"🔍 n8nテスト開始")
    print(f"URL: {url}")
    print(f"ペイロード: {json.dumps(test_payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📊 レスポンス情報:")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスヘッダー: {dict(response.headers)}")
        print(f"レスポンス内容: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ n8nテスト成功！")
            try:
                result = response.json()
                print(f"パース結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                print("レスポンスはJSONではありません")
            return True
        else:
            print(f"\n❌ n8nテスト失敗: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 接続エラー: {e}")
        print("n8nサーバーが起動していない可能性があります")
        return False
    except requests.exceptions.Timeout as e:
        print(f"\n❌ タイムアウトエラー: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ リクエストエラー: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return False

def test_alternative_endpoints():
    """代替エンドポイントのテスト"""
    
    alternative_urls = [
        "https://n8n.xvps.jp/webhook-test/hannan-email-webhook",
        "https://n8n.xvps.jp/webhook/test",
        "https://n8n.xvps.jp/api/webhooks/hannan-email-webhook"
    ]
    
    test_payload = {"test": "ping", "timestamp": datetime.now().isoformat()}
    
    print(f"\n🔍 代替エンドポイントテスト")
    
    for url in alternative_urls:
        print(f"\n--- テスト: {url} ---")
        try:
            response = requests.post(url, json=test_payload, timeout=10)
            print(f"ステータス: {response.status_code}")
            if response.text:
                print(f"レスポンス: {response.text[:200]}")
            if response.status_code == 200:
                print("✅ 接続成功")
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ エラー: {e}")

if __name__ == "__main__":
    print("🚀 n8n Webhook簡易テスト")
    print("=" * 50)
    
    # メインテスト
    main_test_ok = test_n8n_webhook()
    
    # 代替エンドポイントテスト
    test_alternative_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 テスト結果")
    print(f"メインWebhook: {'✅' if main_test_ok else '❌'}")
    
    if not main_test_ok:
        print("\n💡 次のステップ:")
        print("1. n8nサーバーの状態を確認")
        print("2. Webhookワークフローが有効か確認")
        print("3. エンドポイントURLが正しいか確認")
        print("4. ネットワーク接続を確認")

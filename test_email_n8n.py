#!/usr/bin/env python3
# test_email_n8n.py - n8nメール送信テスト

import sys
import os
import requests
import json
from datetime import datetime

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from services.email_send_service import EmailSendService

def test_n8n_connection():
    """n8n接続テスト"""
    print("🔍 n8n接続テスト開始")
    print(f"URL: {Config.N8N_WEBHOOK_URL}")
    
    # テストペイロード
    test_payload = {
        "test": "connection",
        "timestamp": datetime.now().isoformat(),
        "source": "ai-agent-test"
    }
    
    try:
        response = requests.post(
            Config.N8N_WEBHOOK_URL,
            json=test_payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスヘッダー: {dict(response.headers)}")
        print(f"レスポンス内容: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ n8n接続成功")
            return True
        else:
            print(f"❌ n8n接続失敗: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 接続エラー: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ タイムアウト: {e}")
        return False
    except Exception as e:
        print(f"❌ その他のエラー: {e}")
        return False

def test_email_service():
    """EmailSendServiceテスト"""
    print("\n📧 EmailSendServiceテスト開始")
    
    email_service = EmailSendService()
    
    # テストメッセージ
    user_message = "田中さんにメール送って"
    ai_response = "承知いたしました。田中さんにご連絡いたします。"
    
    print(f"テストメッセージ: {user_message}")
    print(f"AI回答: {ai_response}")
    
    # メール送信判定テスト
    should_send = email_service.should_send_email(user_message, ai_response)
    print(f"メール送信判定: {should_send}")
    
    if should_send:
        # メールリクエスト抽出
        email_request = email_service.extract_email_request(user_message, ai_response)
        print(f"メールリクエスト: {json.dumps(email_request, ensure_ascii=False, indent=2)}")
        
        # メール送信実行
        if email_request["should_send"]:
            result = email_service.send_email_via_n8n(email_request)
            print(f"送信結果: {result}")
    
    return should_send

def test_specific_email():
    """具体的なメール送信テスト"""
    print("\n📩 具体的なメール送信テスト")
    
    email_service = EmailSendService()
    
    # パスワードリセット依頼のテスト
    test_cases = [
        {
            "user_message": "田中さんにメールお願いします",
            "ai_response": "パスワードリセットについて田中さんにご連絡いたします。"
        },
        {
            "user_message": "販売管理ソフトのパスワードがわからない",
            "ai_response": "販売管理ソフト「侍」のパスワードリセットについて、システムソリューション課の田中さんにお問い合わせください。"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- テストケース {i} ---")
        user_message = test_case["user_message"]
        ai_response = test_case["ai_response"]
        
        print(f"ユーザー: {user_message}")
        print(f"AI: {ai_response}")
        
        # メール処理実行
        email_sent, final_response = email_service.process_email_request(user_message, ai_response)
        
        print(f"メール送信: {email_sent}")
        print(f"最終回答: {final_response[:200]}...")

def main():
    """メインテスト実行"""
    print("🚀 n8nメール送信総合テスト開始")
    print("=" * 50)
    
    # 1. 設定確認
    print(f"N8N_WEBHOOK_URL: {Config.N8N_WEBHOOK_URL}")
    
    # 2. n8n接続テスト
    connection_ok = test_n8n_connection()
    
    # 3. EmailServiceテスト
    service_ok = test_email_service()
    
    # 4. 具体的なメール送信テスト
    test_specific_email()
    
    print("\n" + "=" * 50)
    print("📋 テスト結果サマリー")
    print(f"n8n接続: {'✅' if connection_ok else '❌'}")
    print(f"EmailService: {'✅' if service_ok else '❌'}")
    
    if not connection_ok:
        print("\n💡 トラブルシューティング:")
        print("1. n8nサーバーが起動しているか確認")
        print("2. Webhookエンドポイントが正しく設定されているか確認")
        print("3. ファイアウォール設定を確認")
        print("4. URLが正しいか確認:")
        print(f"   設定値: {Config.N8N_WEBHOOK_URL}")
        print(f"   期待値: https://n8n.xvps.jp/webhook/hannan-email-webhook")

if __name__ == "__main__":
    main()

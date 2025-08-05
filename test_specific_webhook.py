#!/usr/bin/env python3
# test_specific_webhook.py - 特定のWebhook URLをテスト

import requests
import json
from datetime import datetime

def test_hannan_webhook():
    """特定のn8n Webhookをテスト"""
    
    webhook_url = "https://n8n.xvps.jp/webhook-test/hannan-email-webhook"
    
    # 実際のメール送信データと同じ形式でテスト
    test_payload = {
        "recipient_email": "akamatsu.d@hbm-web.co.jp",
        "recipient_name": "田中さん",
        "email_subject": "【パスワードリセット依頼】勤怠管理システム",
        "email_content": """田中様

お世話になっております。

勤怠管理システムのパスワードリセットをお願いしたく、ご連絡させていただきました。

【依頼内容】
- システム名: 勤怠管理システム
- 依頼者: LINE AIアシスタント  
- 問題: ログインパスワードが不明
- 緊急度: 高

【状況詳細】
有給申請ソフトのログイン情報を忘れてしまった件について...

パスワードの再設定をお願いいたします。
お手数をおかけいたしますが、どうぞよろしくお願いいたします。

【このメールはAIアシスタントから自動送信されています】
生成時刻: """ + datetime.now().strftime('%Y年%m月%d日 %H時%M分'),
        "urgency": "high"
    }
    
    print("🚀 n8n Webhook詳細テストを開始...")
    print(f"📍 URL: {webhook_url}")
    print(f"📧 宛先: {test_payload['recipient_name']} ({test_payload['recipient_email']})")
    print(f"📄 件名: {test_payload['email_subject']}")
    print(f"⚡ 緊急度: {test_payload['urgency']}")
    print("")
    
    try:
        print("📤 リクエスト送信中...")
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'HannanBusinessMachine-AI/1.0'
            }
        )
        
        print(f"📨 ステータスコード: {response.status_code}")
        print(f"📏 レスポンス長: {len(response.text)}文字")
        print("")
        
        if response.status_code == 200:
            print("✅ Webhook接続成功！")
            
            try:
                result = response.json()
                print("📊 レスポンス内容:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result.get("status") == "success":
                    print("")
                    print("🎉 メール送信処理が正常に完了しました！")
                else:
                    print("")
                    print(f"⚠️ 処理完了ですが、ステータスが予期しない値: {result.get('status')}")
                    
            except json.JSONDecodeError:
                print("📄 テキストレスポンス:")
                print(response.text)
                
        elif response.status_code == 404:
            print("❌ Webhook URLが見つかりません")
            print("💡 n8nダッシュボードでWebhook URLを確認してください")
            
        elif response.status_code == 500:
            print("❌ サーバー内部エラー")
            print("💡 n8nワークフローでエラーが発生している可能性があります")
            print(f"📄 エラー詳細: {response.text}")
            
        else:
            print(f"⚠️ 予期しないステータス: {response.status_code}")
            print(f"📄 レスポンス: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー")
        print("💡 n8n.xvps.jpが正常に動作しているか確認してください")
        
    except requests.exceptions.Timeout:
        print("⏰ タイムアウト（30秒）")
        print("💡 n8nの処理に時間がかかっている可能性があります")
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
    
    print("")
    print("🔗 次のステップ:")
    print("1. n8nダッシュボードで実行履歴を確認: https://n8n.xvps.jp")
    print("2. ワークフローがアクティブになっているか確認")
    print("3. Gmail認証が正常に設定されているか確認")
    print("4. AIサーバーでもう一度LINEからテスト")

if __name__ == "__main__":
    test_hannan_webhook()
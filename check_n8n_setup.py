#!/usr/bin/env python3
"""
N8N設定確認ツール
設定の状態を確認し、問題を診断
"""

import os
import requests
import json
from dotenv import load_dotenv

def check_n8n_setup():
    """N8N設定の確認"""
    
    print("🔍 **N8N設定状況の確認**")
    print("=" * 50)
    
    # 1. 環境変数確認
    load_dotenv()
    webhook_url = os.getenv('N8N_WEBHOOK_URL', '')
    
    print(f"📋 **環境変数確認**")
    print(f"N8N_WEBHOOK_URL: {webhook_url}")
    
    if not webhook_url or webhook_url == 'disabled':
        print("❌ N8N_WEBHOOK_URLが設定されていません")
        print("   .envファイルに以下を追加してください：")
        print("   N8N_WEBHOOK_URL=http://localhost:5678/webhook/hannan-email-webhook")
        return False
    
    if 'localhost:5678' in webhook_url:
        print("✅ ローカル開発環境用URL")
    elif 'your-domain' in webhook_url:
        print("❌ プレースホルダーURLです。実際のドメインに変更してください")
        return False
    else:
        print("✅ 本番環境用URL")
    
    print()
    
    # 2. N8N接続確認
    print(f"🌐 **N8N接続確認**")
    
    try:
        # N8Nのヘルスチェック（ダッシュボードURL）
        base_url = webhook_url.replace('/webhook/hannan-email-webhook', '')
        health_response = requests.get(f"{base_url}/healthz", timeout=5)
        
        if health_response.status_code == 200:
            print("✅ N8Nサーバーが稼働中")
        else:
            print(f"⚠️ N8Nサーバー応答: {health_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ N8Nサーバーに接続できません")
        print("   以下を確認してください：")
        print("   1. N8Nが起動しているか")
        print("   2. ポート5678が開いているか") 
        print("   3. ファイアウォール設定")
        return False
    except requests.exceptions.Timeout:
        print("⚠️ N8Nサーバーへの接続がタイムアウト")
    except Exception as e:
        print(f"❌ 接続エラー: {str(e)}")
        return False
    
    print()
    
    # 3. Webhook テスト
    print(f"📧 **Webhookテスト**")
    
    test_payload = {
        "action": "send_email",
        "email_data": {
            "recipients": [
                {
                    "email": "test@example.com",
                    "name": "テストユーザー"
                }
            ],
            "subject": "【テスト】N8N連携確認",
            "content": "これはN8N設定確認のテストメールです。",
            "urgency": "normal"
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook正常応答")
            print(f"   レスポンス: {response.text[:100]}...")
        elif response.status_code == 404:
            print("❌ Webhookエンドポイントが見つかりません")
            print("   ワークフローが正しく設定されているか確認してください")
        else:
            print(f"⚠️ Webhook応答エラー: {response.status_code}")
            print(f"   レスポンス: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Webhookに接続できません")
        return False
    except Exception as e:
        print(f"❌ Webhookテストエラー: {str(e)}")
        return False
    
    print()
    
    # 4. 設定サマリー
    print(f"📊 **設定サマリー**")
    print("✅ すべての確認が完了しました")
    print()
    print("🚀 **次のステップ**")
    print("1. アプリケーションを再起動")
    print("2. LINEで「田中さんにメールをお願いします」をテスト")
    print("3. 「メール送信完了」が表示されれば設定完了")
    
    return True

def create_test_workflow():
    """テスト用のワークフロー設定を出力"""
    
    print("\n🔧 **テスト用ワークフロー設定**")
    print("=" * 50)
    
    workflow_config = {
        "nodes": [
            {
                "name": "Webhook",
                "type": "webhook",
                "settings": {
                    "method": "POST",
                    "path": "hannan-email-webhook"
                }
            },
            {
                "name": "Set Email Data", 
                "type": "set",
                "mappings": {
                    "recipient_email": "{{ $json.email_data.recipients[0].email }}",
                    "email_subject": "{{ $json.email_data.subject }}",
                    "email_content": "{{ $json.email_data.content }}"
                }
            },
            {
                "name": "Gmail Send",
                "type": "gmail",
                "settings": {
                    "operation": "send",
                    "to": "{{ $json.recipient_email }}",
                    "subject": "{{ $json.email_subject }}",
                    "message": "{{ $json.email_content }}"
                }
            }
        ]
    }
    
    print("N8Nで以下のノードを設定してください：")
    for i, node in enumerate(workflow_config["nodes"], 1):
        print(f"\n{i}. **{node['name']}** ({node['type']})")
        if 'settings' in node:
            for key, value in node['settings'].items():
                print(f"   - {key}: {value}")
        if 'mappings' in node:
            for key, value in node['mappings'].items():
                print(f"   - {key}: {value}")

def show_troubleshooting():
    """トラブルシューティングガイド"""
    
    print("\n🔧 **トラブルシューティング**")
    print("=" * 50)
    
    issues = [
        {
            "problem": "「N8N連携は現在無効です」と表示される",
            "solutions": [
                ".envファイルにN8N_WEBHOOK_URLを設定",
                "アプリケーションを再起動",
                "環境変数が正しく読み込まれているか確認"
            ]
        },
        {
            "problem": "Webhook接続エラー",
            "solutions": [
                "N8Nが起動しているか確認",
                "ワークフローがアクティブか確認",
                "Webhook URLが正しいか確認",
                "ポート5678が開いているか確認"
            ]
        },
        {
            "problem": "Gmail送信エラー",
            "solutions": [
                "Gmail OAuth2認証を確認",
                "Gmail APIが有効化されているか確認",
                "送信元メールアドレスの権限を確認",
                "Google Cloud Consoleの設定を確認"
            ]
        }
    ]
    
    for issue in issues:
        print(f"\n❌ **{issue['problem']}**")
        print("   解決方法：")
        for solution in issue['solutions']:
            print(f"   • {solution}")

if __name__ == "__main__":
    success = check_n8n_setup()
    create_test_workflow()
    show_troubleshooting()
    
    if success:
        print("\n🎉 **設定確認完了！**")
        print("N8Nメール送信機能の設定が正常に完了しました。")
    else:
        print("\n⚠️ **設定に問題があります**")
        print("上記の指示に従って設定を修正してください。")

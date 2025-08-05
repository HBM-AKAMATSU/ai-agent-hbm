#!/usr/bin/env python3
# fix_n8n_webhook.py - n8nメール送信Webhook修復ツール

import json
import requests
from datetime import datetime

class N8NWebhookFixer:
    """n8nメール送信Webhook修復ツール"""
    
    def __init__(self):
        self.base_url = "https://n8n.xvps.jp"
        self.test_endpoints = [
            "/webhook/hannan-email-webhook",
            "/webhook-test/hannan-email-webhook", 
            "/webhook/hannan-email",
            "/webhook/email",
            "/api/webhooks/hannan-email-webhook"
        ]
        
    def test_endpoint(self, endpoint_path):
        """指定されたエンドポイントをテスト"""
        url = f"{self.base_url}{endpoint_path}"
        
        test_payload = {
            "recipient_email": "test@example.com",
            "recipient_name": "テストユーザー", 
            "email_subject": "【テスト】接続確認",
            "email_content": "n8n接続テストです",
            "urgency": "normal",
            "test": True,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(url, json=test_payload, timeout=10)
            return {
                "url": url,
                "status_code": response.status_code,
                "response_text": response.text[:200],
                "success": response.status_code == 200,
                "error": None
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "response_text": "",
                "success": False,
                "error": str(e)
            }
    
    def find_working_endpoint(self):
        """動作するエンドポイントを検索"""
        print("🔍 n8nエンドポイント検索中...")
        
        working_endpoints = []
        
        for endpoint in self.test_endpoints:
            print(f"  テスト中: {endpoint}")
            result = self.test_endpoint(endpoint)
            
            print(f"    ステータス: {result['status_code']}")
            if result['error']:
                print(f"    エラー: {result['error']}")
            elif result['response_text']:
                print(f"    レスポンス: {result['response_text'][:100]}...")
            
            if result['success']:
                working_endpoints.append(result)
                print(f"    ✅ 動作確認")
            else:
                print(f"    ❌ 失敗")
        
        return working_endpoints
    
    def generate_workflow_template(self):
        """n8nワークフローテンプレートを生成"""
        workflow_template = {
            "name": "Hannan Business Machine Email Webhook",
            "nodes": [
                {
                    "parameters": {
                        "path": "hannan-email-webhook",
                        "options": {},
                        "httpMethod": "POST"
                    },
                    "id": "webhook-node",
                    "name": "Email Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [300, 300]
                },
                {
                    "parameters": {
                        "operation": "send",
                        "to": "={{ $json.recipient_email }}",
                        "subject": "={{ $json.email_subject }}",
                        "message": "={{ $json.email_content }}",
                        "senderName": "阪南ビジネスマシン AIアシスタント"
                    },
                    "id": "gmail-node",
                    "name": "Send Email",
                    "type": "n8n-nodes-base.gmail",
                    "typeVersion": 1,
                    "position": [520, 300]
                },
                {
                    "parameters": {
                        "values": {
                            "string": [
                                {
                                    "name": "status",
                                    "value": "success"
                                },
                                {
                                    "name": "message", 
                                    "value": "メール送信処理を開始しました"
                                }
                            ]
                        },
                        "options": {}
                    },
                    "id": "response-node",
                    "name": "Response",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 1,
                    "position": [740, 300]
                }
            ],
            "connections": {
                "Email Webhook": {
                    "main": [
                        [
                            {
                                "node": "Send Email",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Send Email": {
                    "main": [
                        [
                            {
                                "node": "Response", 
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "active": True,
            "settings": {},
            "versionId": "1"
        }
        
        return workflow_template
    
    def create_env_update_instructions(self, working_url=None):
        """環境変数更新手順を生成"""
        instructions = """
# .env ファイル更新手順

## 動作するエンドポイントが見つかった場合:
"""
        if working_url:
            instructions += f"""
N8N_WEBHOOK_URL={working_url}
"""
        else:
            instructions += """
# 動作するエンドポイントが見つからなかった場合:
N8N_WEBHOOK_URL=disabled

# 新しいワークフロー作成後:
# N8N_WEBHOOK_URL=https://n8n.xvps.jp/webhook/new-hannan-email-webhook
"""
        
        return instructions
    
    def run_diagnosis(self):
        """総合診断を実行"""
        print("🚀 n8nメール送信Webhook診断開始")
        print("=" * 60)
        
        # エンドポイント検索
        working_endpoints = self.find_working_endpoint()
        
        print(f"\n📊 診断結果:")
        print(f"テスト済みエンドポイント数: {len(self.test_endpoints)}")
        print(f"動作確認できたエンドポイント数: {len(working_endpoints)}")
        
        if working_endpoints:
            print(f"\n✅ 動作するエンドポイントが見つかりました:")
            for endpoint in working_endpoints:
                print(f"  - {endpoint['url']}")
            
            # 最初の動作するエンドポイントで.env更新提案
            best_endpoint = working_endpoints[0]['url']
            print(f"\n💡 推奨設定:")
            print(f"N8N_WEBHOOK_URL={best_endpoint}")
            
        else:
            print(f"\n❌ 動作するエンドポイントが見つかりませんでした")
            print(f"\n📝 必要な作業:")
            print(f"1. n8nダッシュボードにアクセス: {self.base_url}")
            print(f"2. 新しいメール送信ワークフローを作成")
            print(f"3. 以下のテンプレートを使用してワークフロー設定")
            
            # ワークフローテンプレート出力
            template = self.generate_workflow_template()
            print(f"\n📄 ワークフローテンプレート:")
            print(json.dumps(template, ensure_ascii=False, indent=2))
        
        # 環境変数更新手順
        working_url = working_endpoints[0]['url'] if working_endpoints else None
        env_instructions = self.create_env_update_instructions(working_url)
        print(f"\n🔧 環境変数更新手順:")
        print(env_instructions)
        
        return len(working_endpoints) > 0

def main():
    """メイン実行関数"""
    fixer = N8NWebhookFixer()
    success = fixer.run_diagnosis()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ n8nメール送信機能は修復可能です")
        print("上記の推奨設定で.envファイルを更新してください")
    else:
        print("🔧 n8nワークフローの再作成が必要です")
        print("手順に従ってワークフローを作成してください")

if __name__ == "__main__":
    main()

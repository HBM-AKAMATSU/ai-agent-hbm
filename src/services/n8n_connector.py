# src/services/n8n_connector.py
import requests
from config import Config
from datetime import datetime

class N8NConnector:
    def __init__(self):
        self.webhook_url = Config.N8N_WEBHOOK_URL

    def execute_task(self, task_description: str) -> str:
        """n8nのWebhookにタスク実行を依頼する"""
        # N8N URL チェック
        if not self.webhook_url or self.webhook_url == "disabled" or "your-n8n-instance" in self.webhook_url:
            return "n8n連携は現在無効です。手動でタスクを実行してください。"

        # n8nに送信するデータペイロード
        payload = {
            "task_description": task_description,
            "timestamp": datetime.now().isoformat()
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10  # 10秒でタイムアウト
            )

            if response.status_code == 200:
                # n8nからの応答メッセージを取得（設定されていれば）
                result = response.json()
                message = result.get("message", "n8nでタスクを実行しました。")
                return f"✅ {message}"
            else:
                return f"❌ タスク実行でエラーが発生しました。(ステータスコード: {response.status_code})"

        except requests.exceptions.ConnectionError:
            return "❌ n8nサーバーに接続できません。URLを確認してください。"
        except requests.exceptions.Timeout:
            return "❌ n8nサーバーからの応答がタイムアウトしました。"
        except requests.exceptions.RequestException as e:
            return f"❌ n8nとの連携中にエラーが発生しました: {str(e)[:100]}..."
# src/services/n8n_workflow_service.py - N8Nワークフロー連携サービス

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
from config import Config

class N8NWorkflowService:
    """N8Nワークフロー連携サービス"""
    
    def __init__(self):
        self.webhook_url = Config.N8N_WEBHOOK_URL
        self.timeout = 30  # 30秒タイムアウト
    
    def trigger_report_email(self, report_data: Dict[str, Any]) -> str:
        """レポートメール配信のトリガー"""
        # N8N URL チェック
        if not self.webhook_url or self.webhook_url == "disabled" or "your-n8n-instance" in self.webhook_url:
            return "N8N連携は現在無効です。レポートを手動で配信してください。"
        
        # メール配信用のペイロード準備
        payload = {
            "action": "send_report_email",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "report_type": report_data.get("type", "daily"),
                "report_title": report_data.get("title", "営業レポート"),
                "report_content": report_data.get("content", ""),
                "recipient": report_data.get("recipient", "部長"),
                "sender": "営業支援AI みなみちゃん",
                "priority": report_data.get("priority", "normal"),
                "company": "阪南ビジネスマシン株式会社",
                "website": "https://hbm-web.co.jp/"
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json() if response.text else {}
                message = result.get("message", "レポートメールの配信を開始しました")
                return f"✅ {message}"
            elif response.status_code == 202:
                return "✅ レポートメール配信リクエストを受け付けました。処理中です..."
            else:
                return f"⚠️ メール配信リクエストでエラーが発生しました。(ステータス: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⚠️ N8Nサーバーとの通信がタイムアウトしました。処理は継続されている可能性があります。"
        except requests.exceptions.ConnectionError:
            return "❌ N8Nサーバーに接続できませんでした。サーバーの状態を確認してください。"
        except requests.exceptions.RequestException as e:
            return f"❌ N8Nとの連携中にエラーが発生しました: {str(e)}"
        except Exception as e:
            return f"❌ 予期せぬエラーが発生しました: {str(e)}"
    
    def send_webhook_request(self, data: Dict[str, Any], workflow_type: str = "general") -> str:
        """汎用Webhookリクエスト送信"""
        # N8N URL チェック
        if not self.webhook_url or self.webhook_url == "disabled" or "your-n8n-instance" in self.webhook_url:
            return "N8N連携は現在無効です。"
        
        # 汎用ペイロード準備
        payload = {
            "workflow_type": workflow_type,
            "timestamp": datetime.now().isoformat(),
            "source": "hannan_business_machine_ai",
            "data": data
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json() if response.text else {}
                message = result.get("message", "ワークフローを実行しました")
                return f"✅ {message}"
            else:
                return f"⚠️ ワークフロー実行でエラーが発生しました。(ステータス: {response.status_code})"
                
        except requests.exceptions.RequestException as e:
            return f"❌ N8Nワークフロー実行エラー: {str(e)}"
        except Exception as e:
            return f"❌ 予期せぬエラーが発生しました: {str(e)}"
    
    def format_webhook_data(self, report_content: str, report_type: str = "daily", recipient: str = "部長") -> Dict[str, Any]:
        """Webhookデータのフォーマット"""
        return {
            "type": report_type,
            "title": f"阪南ビジネスマシン {report_type}_report_{datetime.now().strftime('%Y%m%d')}",
            "content": report_content,
            "recipient": recipient,
            "priority": "normal" if report_type == "daily" else "high",
            "generated_at": datetime.now().isoformat(),
            "format": "text",
            "company_info": {
                "name": "阪南ビジネスマシン株式会社",
                "website": "https://hbm-web.co.jp/",
                "department": "官需課"
            }
        }
    
    def trigger_monthly_report_workflow(self, report_content: str, recipients: list = None) -> str:
        """月次レポート配信ワークフローのトリガー"""
        if recipients is None:
            recipients = ["部長", "課長"]
        
        results = []
        for recipient in recipients:
            report_data = self.format_webhook_data(
                report_content, 
                report_type="monthly", 
                recipient=recipient
            )
            result = self.trigger_report_email(report_data)
            results.append(f"{recipient}: {result}")
        
        return "\n".join(results)
    
    def trigger_custom_workflow(self, workflow_name: str, custom_data: Dict[str, Any]) -> str:
        """カスタムワークフローのトリガー"""
        payload = {
            "workflow_name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "custom_data": custom_data,
            "source": "hannan_business_machine_ai"
        }
        
        return self.send_webhook_request(payload, workflow_type="custom")
    
    def check_webhook_status(self) -> str:
        """Webhook接続状態の確認"""
        if not self.webhook_url:
            return "❌ N8N Webhook URLが設定されていません。"
        
        # 簡単なpingテスト
        test_payload = {
            "action": "ping",
            "timestamp": datetime.now().isoformat(),
            "source": "hannan_business_machine_ai"
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=test_payload,
                timeout=10,  # 短いタイムアウト
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return "✅ N8N Webhookサーバーとの接続は正常です。"
            else:
                return f"⚠️ N8N Webhookサーバーからステータス{response.status_code}が返されました。"
                
        except requests.exceptions.Timeout:
            return "⚠️ N8N Webhookサーバーへの接続がタイムアウトしました。"
        except requests.exceptions.ConnectionError:
            return "❌ N8N Webhookサーバーに接続できません。"
        except Exception as e:
            return f"❌ 接続テスト中にエラーが発生しました: {str(e)}"
    
    def execute_sales_automation(self, automation_type: str, sales_data: Dict[str, Any]) -> str:
        """営業自動化ワークフローの実行"""
        automation_workflows = {
            "lead_nurturing": "リード育成ワークフロー",
            "follow_up_reminder": "フォローアップリマインダー",
            "proposal_generation": "提案書生成",
            "customer_satisfaction_survey": "顧客満足度調査",
            "pipeline_update": "パイプライン更新通知"
        }
        
        if automation_type not in automation_workflows:
            return f"❌ 未対応の自動化タイプです: {automation_type}"
        
        workflow_data = {
            "automation_type": automation_type,
            "automation_name": automation_workflows[automation_type],
            "sales_data": sales_data,
            "company": "阪南ビジネスマシン株式会社",
            "department": "官需課"
        }
        
        result = self.send_webhook_request(workflow_data, workflow_type="sales_automation")
        return f"{automation_workflows[automation_type]}を実行: {result}"
    
    def send_daily_summary_to_team(self, summary_data: Dict[str, Any]) -> str:
        """チーム向け日次サマリー配信"""
        team_members = ["高見", "辻川", "小濱"]
        
        # チーム全体向けの情報を準備
        team_payload = {
            "action": "team_daily_summary",
            "summary_data": summary_data,
            "team_members": team_members,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "company": "阪南ビジネスマシン株式会社"
        }
        
        return self.send_webhook_request(team_payload, workflow_type="team_communication")
    
    def get_integration_examples(self) -> Dict[str, str]:
        """N8N連携の使用例を返す"""
        return {
            "レポート配信": "「月次レポートを部長に送信して」",
            "リマインダー設定": "「明日のフォローアップを設定して」",
            "顧客満足度調査": "「主要顧客に満足度調査を送って」",
            "チーム通知": "「今日のサマリーをチームに共有して」",
            "自動化設定": "「新規リードの育成ワークフローを開始して」"
        }
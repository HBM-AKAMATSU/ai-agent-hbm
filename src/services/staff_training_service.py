# src/services/staff_training_service.py
"""
職員研修管理サービス
A病院の職員研修履歴・効果分析を提供
"""

import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from collections import defaultdict

class StaffTrainingService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.training_data = self._load_training_data()
        
    def _load_training_data(self):
        """職員研修データの読み込み"""
        try:
            with open("src/data/dummy_data/staff_training_records.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _add_demo_disclaimer(self, response: str) -> str:
        """デモ版・電子カルテ連携前提の注記を追加"""
        disclaimer = """

---
⚠️ **デモ版システムについて**
• このシステムはデモ版です。実際の運用時は人事システム・研修管理システムとの連携が前提となります。
• 表示データは仮想データです。実運用時はリアルタイムの人事データを参照します。
• 本格運用には以下の技術統合が必要：
  - 人事システムAPI連携
  - 研修管理システム連携
  - セキュア認証・プライバシー保護システム
  - 勤怠管理システム統合

🏥 **A病院 Smart Hospital AI - Staff Training Analysis Module**"""
        
        return response + disclaimer
    
    def analyze_staff_training(self, query: str) -> str:
        """職員研修分析（メインエントリーポイント）"""
        
        training_db = self.training_data.get("staff_training_database", {})
        
        # 職員名の抽出（簡単なパターンマッチング）
        staff_names = ["田中 美咲", "佐藤 健一", "山田 裕子"]
        target_staff = None
        for name in staff_names:
            if name in query:
                target_staff = name
                break
        
        if target_staff:
            return self._analyze_individual_training(target_staff, query)
        else:
            return self._analyze_general_training(query)
    
    def _analyze_individual_training(self, staff_name: str, query: str) -> str:
        """個別職員の研修分析"""
        
        training_db = self.training_data.get("staff_training_database", {})
        staff_record = None
        
        # 該当職員の記録を検索
        for record in training_db.get("individual_records", []):
            if record.get("name") == staff_name:
                staff_record = record
                break
        
        if not staff_record:
            return self._add_demo_disclaimer(f"申し訳ありません。職員「{staff_name}」の研修記録が見つかりませんでした。")
        
        prompt = f"""
        あなたはA病院の人事・研修担当責任者です。以下の職員研修記録に基づき、ユーザーの質問（「{query}」）に対し、**自然な会話のような文章で、具体的に分析報告**を行ってください。
        **「🏥 A病院 職員研修分析レポート」のようなレポートタイトルや、「## 👤 **対象職員プロファイル**」のようなセクションヘッダーは、回答に含めないでください。**
        重要な情報や分析結果は、簡潔な文章で分かりやすく説明してください。箇条書きは、情報が特に多く、視覚的な整理が有効な場合にのみ使用してください。

        # 職員情報
        **職員名**: {staff_record.get("name", "N/A")}
        **所属**: {staff_record.get("department", "N/A")}
        **職位**: {staff_record.get("position", "N/A")}
        **職員ID**: {staff_record.get("staff_id", "N/A")}

        # 研修履歴詳細
        {json.dumps(staff_record.get("training_history", []), ensure_ascii=False, indent=2)}

        # A病院全体の研修効果指標
        {json.dumps(training_db.get("training_effectiveness_analysis", {}), ensure_ascii=False, indent=2)}

        # 質問
        {query}

        # 回答:
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院職員研修分析中にエラーが発生しました: {e}"
    
    def _analyze_general_training(self, query: str) -> str:
        """全体的な研修分析"""
        
        training_db = self.training_data.get("staff_training_database", {})
        
        prompt = f"""
        あなたはA病院の人事・研修企画責任者です。以下のA病院の研修実績データに基づき、ユーザーの質問（「{query}」）に対し、**自然な会話のような文章で、組織的な研修効果分析報告**を行ってください。
        **「🏥 A病院 組織研修分析レポート」のようなレポートタイトルや、「## 📈 **研修実績概要**」のようなセクションヘッダーは、回答に含めないでください。**
        重要な情報や分析結果は、簡潔な文章で分かりやすく説明してください。箇条書きは、情報が特に多く、視覚的な整理が有効な場合にのみ使用してください。

        # A病院研修実績サマリー
        - 分析期間: {training_db.get("analysis_period", "N/A")}
        - 総職員数: {training_db.get("total_staff", "N/A")}名
        - 研修実施セッション数: {training_db.get("total_training_sessions", "N/A")}回

        # 研修効果分析指標
        {json.dumps(training_db.get("training_effectiveness_analysis", {}), ensure_ascii=False, indent=2)}

        # 代表的研修事例（職員の成果）
        {json.dumps([record.get("training_history", [{}])[0] for record in training_db.get("individual_records", [])], ensure_ascii=False, indent=2)}

        # 質問
        {query}

        # 回答:
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院研修分析中にエラーが発生しました: {e}"
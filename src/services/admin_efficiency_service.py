# src/services/admin_efficiency_service.py
"""
事務業務効率化分析サービス (FR-09)
スタッフ別業務処理能力分析、エラー率・患者満足度の相関分析、業務改善提案
"""

import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from collections import defaultdict
import statistics

class AdminEfficiencyService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.staff_data = self._load_staff_data()
        
    def _load_staff_data(self):
        """スタッフ実績データの読み込み"""
        try:
            data_path = "src/data/dummy_data/staff_performance.json"
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)["staff_performance"]
        except FileNotFoundError:
            return []
    
    def _add_ehr_integration_note(self, response: str) -> str:
        """電子カルテ連携前提機能の注釈を追加"""
        note = """
        
⚠️ **この機能は電子カルテシステムとの連携が前提の回答です。**
📋 実装時には以下が必要: 
• 人事管理システム連携
• 業務ログ自動収集
• 患者満足度調査システム
• 研修管理システム連携"""
        
        return response + note
    
    def analyze_staff_productivity(self, query: str) -> str:
        """スタッフ別業務処理能力分析"""
        # 部署別・個人別実績分析
        dept_performance = defaultdict(lambda: {
            "staff_list": [],
            "avg_procedures": 0,
            "avg_satisfaction": 0,
            "avg_error_rate": 0,
            "total_staff": 0
        })
        
        individual_performance = {}
        
        for record in self.staff_data:
            dept = record.get("department", "不明")
            staff_id = record.get("staff_id", "不明")
            staff_name = record.get("staff_name", "不明")
            procedures = record.get("procedures_count", 0)
            satisfaction = record.get("patient_satisfaction_score", 0)
            error_rate = record.get("error_rate", 0)
            overtime = record.get("overtime_hours", 0)
            
            # 個人実績の蓄積
            if staff_id not in individual_performance:
                individual_performance[staff_id] = {
                    "name": staff_name,
                    "department": dept,
                    "monthly_data": []
                }
            
            individual_performance[staff_id]["monthly_data"].append({
                "month": record.get("month", ""),
                "procedures": procedures,
                "satisfaction": satisfaction,
                "error_rate": error_rate,
                "overtime": overtime
            })
        
        # 個人平均値の計算
        staff_averages = {}
        for staff_id, data in individual_performance.items():
            monthly_data = data["monthly_data"]
            if monthly_data:
                staff_averages[staff_id] = {
                    "name": data["name"],
                    "department": data["department"],
                    "avg_procedures": round(statistics.mean([d["procedures"] for d in monthly_data]), 1),
                    "avg_satisfaction": round(statistics.mean([d["satisfaction"] for d in monthly_data]), 1),
                    "avg_error_rate": round(statistics.mean([d["error_rate"] for d in monthly_data]), 4),
                    "avg_overtime": round(statistics.mean([d["overtime"] for d in monthly_data]), 1)
                }
        
        # 部署別集計
        for staff_id, data in staff_averages.items():
            dept = data["department"]
            dept_performance[dept]["staff_list"].append(staff_id)
            dept_performance[dept]["total_staff"] += 1
        
        # 部署平均の計算
        for dept in dept_performance:
            staff_in_dept = [staff_averages[sid] for sid in dept_performance[dept]["staff_list"]]
            if staff_in_dept:
                dept_performance[dept]["avg_procedures"] = round(
                    statistics.mean([s["avg_procedures"] for s in staff_in_dept]), 1
                )
                dept_performance[dept]["avg_satisfaction"] = round(
                    statistics.mean([s["avg_satisfaction"] for s in staff_in_dept]), 1
                )
                dept_performance[dept]["avg_error_rate"] = round(
                    statistics.mean([s["avg_error_rate"] for s in staff_in_dept]), 4
                )
        
        # トップパフォーマーの特定（医事課に限定）
        admin_staff = {k: v for k, v in staff_averages.items() if v["department"] == "医事課"}
        
        if admin_staff:
            # 処理件数トップ3
            top_performers = sorted(admin_staff.items(), 
                                  key=lambda x: x[1]["avg_procedures"], reverse=True)[:3]
            # エラー率最少3名
            low_error_staff = sorted(admin_staff.items(), 
                                   key=lambda x: x[1]["avg_error_rate"])[:3]
        else:
            top_performers = []
            low_error_staff = []
        
        prompt = f"""
        あなたはA病院の人事・業務改善担当者です。以下のスタッフ実績データを基に、生産性向上提案を行ってください。
        
        # 部署別業務実績
        {dict(dept_performance)}
        
        # 医事課トップパフォーマー（処理件数）
        {dict(top_performers)}
        
        # 医事課低エラー率スタッフ
        {dict(low_error_staff)}
        
        # 質問
        {query}
        
        # 回答形式
        1. **生産性分析**: 部署別・個人別の処理能力評価
        2. **ベストプラクティス**: 高パフォーマーの成功要因分析
        3. **改善機会**: 生産性向上が期待できるスタッフと部署
        4. **育成提案**: 具体的なスキルアップ計画
        5. **システム改善**: 業務効率化のためのIT活用提案
        
        実際の人事評価・育成計画に活用できる具体的な提案を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"スタッフ生産性分析中にエラーが発生しました: {e}"
    
    def analyze_error_correlation(self, query: str) -> str:
        """エラー率・患者満足度の相関分析"""
        # エラー率と満足度の相関データ準備
        correlation_data = []
        
        for record in self.staff_data:
            if record.get("department") in ["医事課", "看護部"]:  # 患者接点の多い部署
                correlation_data.append({
                    "staff_id": record.get("staff_id", ""),
                    "department": record.get("department", ""),
                    "error_rate": record.get("error_rate", 0),
                    "satisfaction": record.get("patient_satisfaction_score", 0),
                    "procedures": record.get("procedures_count", 0),
                    "overtime": record.get("overtime_hours", 0)
                })
        
        # エラー率区分別満足度
        error_categories = {
            "低エラー": {"range": "< 2%", "data": []},
            "標準エラー": {"range": "2-5%", "data": []},
            "高エラー": {"range": "> 5%", "data": []}
        }
        
        for data in correlation_data:
            error_rate = data["error_rate"]
            if error_rate < 0.02:
                error_categories["低エラー"]["data"].append(data)
            elif error_rate <= 0.05:
                error_categories["標準エラー"]["data"].append(data)
            else:
                error_categories["高エラー"]["data"].append(data)
        
        # カテゴリ別平均満足度計算
        for category in error_categories:
            data_list = error_categories[category]["data"]
            if data_list:
                avg_satisfaction = statistics.mean([d["satisfaction"] for d in data_list])
                error_categories[category]["avg_satisfaction"] = round(avg_satisfaction, 1)
                error_categories[category]["staff_count"] = len(data_list)
            else:
                error_categories[category]["avg_satisfaction"] = 0
                error_categories[category]["staff_count"] = 0
        
        # 残業時間とエラー率の関係
        overtime_analysis = defaultdict(list)
        for data in correlation_data:
            overtime = data["overtime"]
            if overtime < 20:
                overtime_analysis["少残業"].append(data["error_rate"])
            elif overtime < 35:
                overtime_analysis["標準残業"].append(data["error_rate"])
            else:
                overtime_analysis["長時間残業"].append(data["error_rate"])
        
        overtime_error_rates = {}
        for category, error_rates in overtime_analysis.items():
            if error_rates:
                overtime_error_rates[category] = round(statistics.mean(error_rates), 4)
        
        prompt = f"""
        あなたはA病院の品質管理・患者満足度向上担当者です。以下の相関分析データを基に、改善提案を行ってください。
        
        # エラー率別患者満足度
        {dict(error_categories)}
        
        # 残業時間別平均エラー率
        {overtime_error_rates}
        
        # 質問
        {query}
        
        # 回答形式
        1. **相関分析結果**: エラー率と患者満足度の関係性
        2. **要因分析**: エラー増加・満足度低下の主要因
        3. **リスク要因**: 残業時間等がエラー率に与える影響
        4. **改善戦略**: エラー削減と満足度向上の統合的アプローチ
        5. **予防策**: エラー発生を未然に防ぐシステム改善
        
        医療安全と患者満足度の両立を図る実践的な改善策を提示してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"エラー相関分析中にエラーが発生しました: {e}"
    
    def analyze_skill_development(self, query: str) -> str:
        """スキルアップ支援分析"""
        # 研修時間と業績の関係
        training_performance = []
        
        for record in self.staff_data:
            if record.get("department") == "医事課":
                training_performance.append({
                    "staff_id": record.get("staff_id", ""),
                    "training_hours": record.get("training_hours", 0),
                    "procedures": record.get("procedures_count", 0),
                    "error_rate": record.get("error_rate", 0),
                    "satisfaction": record.get("patient_satisfaction_score", 0)
                })
        
        # 研修時間による効果分析
        training_categories = {
            "積極研修": {"range": "15時間以上", "data": []},
            "標準研修": {"range": "8-14時間", "data": []},
            "最小研修": {"range": "8時間未満", "data": []}
        }
        
        for data in training_performance:
            training_hours = data["training_hours"]
            if training_hours >= 15:
                training_categories["積極研修"]["data"].append(data)
            elif training_hours >= 8:
                training_categories["標準研修"]["data"].append(data)
            else:
                training_categories["最小研修"]["data"].append(data)
        
        # カテゴリ別効果測定
        for category in training_categories:
            data_list = training_categories[category]["data"]
            if data_list:
                training_categories[category].update({
                    "avg_procedures": round(statistics.mean([d["procedures"] for d in data_list]), 1),
                    "avg_error_rate": round(statistics.mean([d["error_rate"] for d in data_list]), 4),
                    "staff_count": len(data_list)
                })
        
        # 改善が必要なスタッフの特定
        improvement_needed = []
        for data in training_performance:
            if (data["error_rate"] > 0.05 or  # エラー率5%以上
                data["procedures"] < 150 or  # 処理件数が平均以下
                data["satisfaction"] < 3.5):  # 満足度が低い
                improvement_needed.append(data)
        
        prompt = f"""
        あなたはA病院の人材開発・教育担当者です。以下の研修効果データを基に、スキルアップ計画を提案してください。
        
        # 研修時間別業績
        {dict(training_categories)}
        
        # スキルアップが必要なスタッフ数
        改善対象者: {len(improvement_needed)}名
        
        # 質問
        {query}
        
        # 回答形式
        1. **研修効果分析**: 研修時間と業務成果の関係
        2. **スキルギャップ**: 現状のスキル不足領域の特定
        3. **個別育成計画**: 対象者別の具体的研修プログラム
        4. **集合研修企画**: 部署全体のスキル底上げ策
        5. **効果測定**: 研修成果を評価する指標と方法
        
        実際の人材育成に活用できる具体的で実現可能な研修計画を提示してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"スキル開発分析中にエラーが発生しました: {e}"
    
    def query_admin_efficiency(self, query: str) -> str:
        """事務効率化分析のメインエントリーポイント"""
        query_lower = query.lower()
        
        # キーワードによる機能振り分け
        if any(keyword in query_lower for keyword in ["生産性", "処理能力", "業務量", "効率"]):
            return self.analyze_staff_productivity(query)
        elif any(keyword in query_lower for keyword in ["エラー", "ミス", "満足度", "相関"]):
            return self.analyze_error_correlation(query)
        elif any(keyword in query_lower for keyword in ["研修", "スキル", "教育", "育成"]):
            return self.analyze_skill_development(query)
        else:
            # 汎用的な効率化分析
            return self.analyze_staff_productivity(query)
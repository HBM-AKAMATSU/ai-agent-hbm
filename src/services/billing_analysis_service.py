# src/services/billing_analysis_service.py
"""
診療報酬分析サービス (FR-07)
A病院の査定傾向分析、収益性分析、ベンチマーク比較を提供
"""

import json
import os
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from config import Config
import pandas as pd
from collections import defaultdict

class BillingAnalysisService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.billing_data = self._load_billing_data()
        self.comprehensive_data = self._load_comprehensive_medical_data()
        self.billing_return_data = self._load_billing_return_data()
        
    def _load_billing_data(self):
        """診療報酬データの読み込み"""
        try:
            data_path = "src/data/dummy_data/billing_records.json"
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)["billing_records"]
        except FileNotFoundError:
            return []
    
    def _load_comprehensive_medical_data(self):
        """包括的医療データ読み込み"""
        try:
            with open("src/data/dummy_data/comprehensive_medical_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_billing_return_data(self):
        """診療報酬返戻データ読み込み"""
        try:
            with open("src/data/dummy_data/billing_return_analysis.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _add_ehr_integration_note(self, response: str) -> str:
        """電子カルテ連携前提機能の注記を追加"""
        note = """
        
---
⚠️ **デモ版システムについて**
• このシステムはデモ版です。実際の運用時は電子カルテシステムとの連携が前提となります。
• 表示データは仮想データです。実運用時はリアルタイムの電子カルテデータを参照します。
• 本格運用には以下の技術統合が必要：
  - 電子カルテAPI連携（HL7 FHIR準拠）
  - リアルタイムデータ同期基盤
  - セキュア認証・監査ログシステム
  - 診療報酬請求システム連携

🏥 **A病院 Smart Hospital AI - Billing Analysis Module**"""
        
        return response + note
    
    def analyze_return_trends(self, query: str) -> str:
        """返戻傾向分析（新機能）"""
        
        billing_return = self.billing_return_data.get("billing_return_analysis", {})
        
        prompt = f"""
        あなたはA病院の診療報酬請求分析責任者です。以下のA病院の返戻分析データに基づき、実用的な改善提案を行ってください。

        # A病院の返戻実績データ（{billing_return.get("analysis_period", "N/A")}）
        **全体返戻率**: {billing_return.get("overall_return_rate", "N/A")}%
        **総請求件数**: {billing_return.get("total_claims", "N/A"):,}件
        **返戻件数**: {billing_return.get("total_returns", "N/A"):,}件

        # 返戻率上位処置・手術
        {json.dumps(billing_return.get("top_return_procedures", []), ensure_ascii=False, indent=2)}

        # 返戻率上位疾患コード
        {json.dumps(billing_return.get("return_by_disease_code", []), ensure_ascii=False, indent=2)}

        # 診療科別返戻分析
        {json.dumps(billing_return.get("department_analysis", {}), ensure_ascii=False, indent=2)}

        # 財務インパクト
        {json.dumps(billing_return.get("financial_impact_summary", {}), ensure_ascii=False, indent=2)}

        # 質問
        {query}

        # 回答形式
        🏥 **A病院 診療報酬返戻分析レポート**

        1. **返戻トップ3の詳細分析**
           - 各項目の返戻理由と対策
           - 財務インパクトの評価

        2. **診療科別改善優先度**
           - リスクの高い診療科の特定
           - 具体的改善アクション

        3. **システム的改善提案**
           - 記載品質向上策
           - チェック機能強化案

        4. **期待される改善効果**
           - 返戻率削減目標
           - 収益改善見込み

        実際のA病院データに基づく実践的な改善提案を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"A病院返戻分析中にエラーが発生しました: {e}"
    
    def analyze_assessment_trends(self, query: str) -> str:
        """査定傾向分析（包括的データ統合版）"""
        
        # 包括的データから査定統計を取得
        billing_data = self.comprehensive_data.get("billing_and_revenue", {})
        audit_stats = billing_data.get("audit_statistics", {})
        
        prompt = f"""
        あなたはA病院の医療事務コンサルタントです。以下の査定分析データを基に、実用的な改善提案を行ってください。
        
        # A病院の査定実績データ（2024年上半期）
        **全体査定率**: {audit_stats.get("overall_audit_rate", "N/A")}%
        
        **診療科別査定率**:
        {json.dumps(audit_stats.get("department_audit_rates", {}), ensure_ascii=False, indent=2)}
        
        **主要査定理由（発生頻度順）**:
        {json.dumps(audit_stats.get("common_audit_reasons", []), ensure_ascii=False, indent=2)}
        
        # A病院の月別収益推移
        {json.dumps(billing_data.get("monthly_revenue", {}), ensure_ascii=False, indent=2)}
        
        # DPC分析結果
        {json.dumps(billing_data.get("dpc_analysis", {}), ensure_ascii=False, indent=2)}
        
        # 質問
        {query}
        
        # 回答形式
        🏥 **A病院 査定対策分析レポート**
        
        1. **現状分析**: A病院の査定傾向の特徴を3点で整理
        2. **リスク診療科**: 査定率の高い診療科と要因分析  
        3. **改善提案**: 具体的な対策を優先順位付きで提示
        4. **期待効果**: 改善による収益インパクトの試算
        5. **ベンチマーク**: 同規模病院平均との比較
        
        実際のA病院データに基づく実践的な改善提案を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"査定分析中にエラーが発生しました: {e}"
    
    def analyze_revenue_performance(self, query: str) -> str:
        """収益性分析"""
        # 月別収益分析
        monthly_revenue = defaultdict(lambda: {"total_points": 0, "total_patients": 0, "departments": defaultdict(int)})
        
        for record in self.billing_data:
            month = record.get("visit_date", "")[:7]  # YYYY-MM
            points = record.get("final_points", 0)
            dept = record.get("department", "不明")
            
            monthly_revenue[month]["total_points"] += points
            monthly_revenue[month]["total_patients"] += 1
            monthly_revenue[month]["departments"][dept] += points
        
        # 診療科別収益分析
        dept_revenue = defaultdict(lambda: {"total_points": 0, "patient_count": 0, "avg_points": 0})
        
        for record in self.billing_data:
            dept = record.get("department", "不明")
            points = record.get("final_points", 0)
            
            dept_revenue[dept]["total_points"] += points
            dept_revenue[dept]["patient_count"] += 1
        
        # 平均点数を計算
        for dept in dept_revenue:
            if dept_revenue[dept]["patient_count"] > 0:
                dept_revenue[dept]["avg_points"] = round(
                    dept_revenue[dept]["total_points"] / dept_revenue[dept]["patient_count"], 1
                )
        
        # 最新3ヶ月の収益推移
        recent_months = sorted(monthly_revenue.keys(), reverse=True)[:3]
        recent_data = {month: monthly_revenue[month] for month in recent_months}
        
        prompt = f"""
        あなたはA病院の経営分析担当者です。以下の収益データを基に、経営改善につながる分析を行ってください。
        
        # 診療科別収益実績
        {dict(dept_revenue)}
        
        # 最新3ヶ月の収益推移
        {dict(recent_data)}
        
        # 質問
        {query}
        
        # 回答形式
        1. **収益構造分析**: 主要診療科の収益貢献と患者単価
        2. **トレンド分析**: 最近の収益推移と要因
        3. **収益最適化提案**: 患者単価向上・収益拡大策
        4. **ベンチマーク比較**: 業界標準との比較（推定値）
        5. **アクションプラン**: 具体的な改善ステップ
        
        実際の経営判断に活用できる具体的な数値とアクションを含めてください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"収益分析中にエラーが発生しました: {e}"
    
    def analyze_competitive_benchmarking(self, query: str) -> str:
        """競合比較分析"""
        # 全体KPIの計算
        total_points = sum(record.get("final_points", 0) for record in self.billing_data)
        total_patients = len(self.billing_data)
        avg_points_per_patient = total_points / total_patients if total_patients > 0 else 0
        
        # 査定率の計算
        assessments = [r for r in self.billing_data if r.get("assessment_reduction", 0) > 0]
        assessment_rate = len(assessments) / len(self.billing_data) if self.billing_data else 0
        
        # 診療科別実績
        dept_performance = defaultdict(lambda: {"patients": 0, "revenue": 0})
        for record in self.billing_data:
            dept = record.get("department", "不明")
            points = record.get("final_points", 0)
            dept_performance[dept]["patients"] += 1
            dept_performance[dept]["revenue"] += points
        
        prompt = f"""
        あなたはA病院の経営企画担当者です。以下の実績データを基に、競合他院との比較分析を行ってください。
        
        # A病院の実績
        - 平均患者単価: {avg_points_per_patient:.1f}点
        - 査定率: {assessment_rate:.3f} ({assessment_rate*100:.1f}%)
        - 総患者数: {total_patients:,}人
        - 主要診療科実績: {dict(dept_performance)}
        
        # 質問
        {query}
        
        # 回答形式
        1. **ベンチマーク比較**: 業界平均・地域平均との比較（推定）
        2. **強み・弱み分析**: A病院の競合優位性と課題
        3. **市場ポジショニング**: 地域医療圏での立ち位置
        4. **競合対策**: 差別化戦略と収益向上策
        5. **目標設定**: 実現可能な改善目標値
        
        地域の200床規模急性期病院との比較を前提に、実践的な分析を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"競合分析中にエラーが発生しました: {e}"
    
    def query_billing_analysis(self, query: str) -> str:
        """診療報酬分析のメインエントリーポイント"""
        query_lower = query.lower()
        
        # キーワードによる機能振り分け
        if any(keyword in query_lower for keyword in ["返戻", "返戻率", "処置", "疾患コード", "返戻理由"]):
            return self.analyze_return_trends(query)
        elif any(keyword in query_lower for keyword in ["査定", "減点", "審査"]):
            return self.analyze_assessment_trends(query)
        elif any(keyword in query_lower for keyword in ["収益", "売上", "収入", "点数"]):
            return self.analyze_revenue_performance(query)
        elif any(keyword in query_lower for keyword in ["競合", "比較", "ベンチマーク", "他院"]):
            return self.analyze_competitive_benchmarking(query)
        else:
            # 汎用的な診療報酬分析
            return self.analyze_revenue_performance(query)
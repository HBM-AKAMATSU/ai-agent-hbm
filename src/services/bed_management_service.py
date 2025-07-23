# src/services/bed_management_service.py
"""
病床管理分析サービス (FR-08)
病床稼働率・在院日数の実績分析、診療科別運用パターン分析を提供
"""

import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from collections import defaultdict

class BedManagementService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.bed_data = self._load_bed_data()
        self.comprehensive_data = self._load_comprehensive_medical_data()
        
    def _load_bed_data(self):
        """病床データの読み込み"""
        try:
            data_path = "src/data/dummy_data/bed_data.json"
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)["bed_data"]
        except FileNotFoundError:
            return []
    
    def _load_comprehensive_medical_data(self):
        """包括的医療データ読み込み"""
        try:
            with open("src/data/dummy_data/comprehensive_medical_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _add_ehr_integration_note(self, response: str) -> str:
        """電子カルテ連携前提機能の注釈を追加"""
        note = """
        
⚠️ **この機能は電子カルテシステムとの連携が前提の回答です。**
📋 実装時には以下が必要: 
• 電子カルテAPI連携
• リアルタイムデータ同期  
• 病床管理システム連携
• 入退院管理システム連携"""
        
        return response + note
    
    def analyze_occupancy_performance(self, query: str) -> str:
        """病床稼働率分析（包括的データ統合版）"""
        
        # 包括的データから病床管理情報を取得
        bed_management = self.comprehensive_data.get("bed_management", {})
        performance_metrics = self.comprehensive_data.get("hospital_performance_metrics", {})
        
        prompt = f"""
        あなたはA病院の病床管理担当者として、以下のA病院の実績データを基に、ユーザーの質問に**自然な会話のような文章**で回答してください。
        **「🏥 A病院 病床管理分析レポート」や番号付きのセクションヘッダー（例:「1. 稼働率分析」）は、回答に含めないでください。**
        質問に直接答える形で、重要な分析結果や改善提案を分かりやすく説明してください。
        箇条書きは、情報が特に多い場合や視覚的な整理が必要な場合にのみ使用し、それ以外は文章で表現してください。
        
        # A病院の病床構成・稼働実績
        {json.dumps(bed_management.get("bed_statistics", {}), ensure_ascii=False, indent=2)}
        
        # 診療科別病床稼働状況
        {json.dumps(bed_management.get("occupancy_by_department", {}), ensure_ascii=False, indent=2)}
        
        # 退院調整実績
        {json.dumps(bed_management.get("discharge_coordination", {}), ensure_ascii=False, indent=2)}
        
        # A病院全体実績指標
        - 全体病床稼働率: {performance_metrics.get("bed_occupancy_rate", "N/A")}%
        - 平均在院日数: {performance_metrics.get("average_los", "N/A")}日
        - 総患者数: {performance_metrics.get("total_patients", "N/A")}名
        - 総入院数: {performance_metrics.get("total_admissions", "N/A")}名
        
        # 質問
        {query}
        
        # 回答:
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"病床稼働分析中にエラーが発生しました: {e}"
    
    def analyze_los_optimization(self, query: str) -> str:
        """在院日数最適化分析"""
        # 病床タイプ別在院日数分析
        los_analysis = {}
        for record in self.bed_data:
            bed_type = record.get("bed_type", "不明")
            los = record.get("avg_length_of_stay", 0)
            admissions = record.get("admissions", 0)
            discharges = record.get("discharges", 0)
            month = record.get("month", "")
            
            if bed_type not in los_analysis:
                los_analysis[bed_type] = {"los_data": [], "turnover_data": []}
            
            los_analysis[bed_type]["los_data"].append({"month": month, "los": los})
            if admissions > 0:
                turnover = discharges / admissions
                los_analysis[bed_type]["turnover_data"].append({"month": month, "turnover": turnover})
        
        # 各病床タイプの平均在院日数
        avg_los_by_type = {}
        for bed_type, data in los_analysis.items():
            if data["los_data"]:
                avg_los = sum(d["los"] for d in data["los_data"]) / len(data["los_data"])
                avg_los_by_type[bed_type] = round(avg_los, 1)
        
        # 業界標準との比較（推定値）
        industry_benchmarks = {
            "一般病床": {"standard_los": 14.5, "target_occupancy": 0.85},
            "ICU": {"standard_los": 4.2, "target_occupancy": 0.75},
            "HCU": {"standard_los": 6.8, "target_occupancy": 0.80},
            "回復期リハ病床": {"standard_los": 75.0, "target_occupancy": 0.90},
            "療養病床": {"standard_los": 250.0, "target_occupancy": 0.95}
        }
        
        prompt = f"""
        あなたはA病院の医療安全・質改善担当者として、以下のA病院の在院日数データを基に、ユーザーの質問に**自然な会話のような文章**で回答してください。
        **「🏥 A病院 在院日数最適化レポート」や番号付きのセクションヘッダー（例:「1. 在院日数分析」）は、回答に含めないでください。**
        質問に直接答える形で、重要な分析結果や改善提案を分かりやすく説明してください。
        箇条書きは、情報が特に多い場合や視覚的な整理が必要な場合にのみ使用し、それ以外は文章で表現してください。
        
        # A病院の病床タイプ別平均在院日数
        {avg_los_by_type}
        
        # 業界標準値（参考）
        {industry_benchmarks}
        
        # 質問
        {query}
        
        # 回答:
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"在院日数分析中にエラーが発生しました: {e}"
    
    def analyze_discharge_planning(self, query: str) -> str:
        """退院調整・地域連携分析"""
        # 月別入退院データ
        monthly_flow = defaultdict(lambda: {"admissions": 0, "discharges": 0, "net_flow": 0})
        
        for record in self.bed_data:
            month = record.get("month", "")
            admissions = record.get("admissions", 0)
            discharges = record.get("discharges", 0)
            
            monthly_flow[month]["admissions"] += admissions
            monthly_flow[month]["discharges"] += discharges
            monthly_flow[month]["net_flow"] += (admissions - discharges)
        
        # 病床タイプ別回転率
        turnover_analysis = {}
        for record in self.bed_data:
            bed_type = record.get("bed_type", "不明")
            total_beds = record.get("total_beds", 1)
            admissions = record.get("admissions", 0)
            month = record.get("month", "")
            
            if bed_type not in turnover_analysis:
                turnover_analysis[bed_type] = []
            
            monthly_turnover = admissions / total_beds if total_beds > 0 else 0
            turnover_analysis[bed_type].append({"month": month, "turnover": monthly_turnover})
        
        # 平均回転率計算
        avg_turnover = {}
        for bed_type, data in turnover_analysis.items():
            if data:
                avg_rate = sum(d["turnover"] for d in data) / len(data)
                avg_turnover[bed_type] = round(avg_rate, 2)
        
        prompt = f"""
        あなたはA病院の地域連携・退院調整担当者として、以下のA病院の実績データを基に、ユーザーの質問に**自然な会話のような文章**で回答してください。
        **「🏥 A病院 退院調整・地域連携分析レポート」や番号付きのセクションヘッダー（例:「1. 入退院動向分析」）は、回答に含めないでください。**
        質問に直接答える形で、重要な分析結果や改善提案を分かりやすく説明してください。
        箇条書きは、情報が特に多い場合や視覚的な整理が必要な場合にのみ使用し、それ以外は文章で表現してください。
        
        # A病院の月別入退院動向
        {dict(monthly_flow)}
        
        # A病院の病床タイプ別月間回転率
        {avg_turnover}
        
        # 質問
        {query}
        
        # 回答:
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"退院調整分析中にエラーが発生しました: {e}"
    
    def query_bed_management(self, query: str) -> str:
        """病床管理分析のメインエントリーポイント"""
        query_lower = query.lower()
        
        # キーワードによる機能振り分け
        if any(keyword in query_lower for keyword in ["稼働率", "占床率", "ベッド", "病床"]):
            return self.analyze_occupancy_performance(query)
        elif any(keyword in query_lower for keyword in ["在院日数", "平均在院", "los", "滞在"]):
            return self.analyze_los_optimization(query)
        elif any(keyword in query_lower for keyword in ["退院調整", "地域連携", "転院", "在宅"]):
            return self.analyze_discharge_planning(query)
        else:
            # 汎用的な病床管理分析
            return self.analyze_occupancy_performance(query)
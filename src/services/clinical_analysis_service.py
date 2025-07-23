# src/services/clinical_analysis_service.py
"""
診療実績・治療成績分析サービス
急性心筋梗塞などの疾患別治療成績、症例数分析を提供
"""

import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from collections import defaultdict
import random

class ClinicalAnalysisService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.clinical_data = self._generate_clinical_summary()
        
    def _generate_clinical_summary(self):
        """模擬的な診療実績データを生成"""
        return {
            "急性心筋梗塞": {
                "年間症例数": 45,
                "年齢別": {
                    "50代": {"症例数": 8, "入院日数平均": 12.3, "治療成功率": 0.95},
                    "60代": {"症例数": 18, "入院日数平均": 14.1, "治療成功率": 0.92},
                    "70代": {"症例数": 15, "入院日数平均": 16.8, "治療成功率": 0.89},
                    "80代以上": {"症例数": 4, "入院日数平均": 19.2, "治療成功率": 0.85}
                },
                "治療方法別": {
                    "PCI（経皮的冠動脈形成術）": {"症例数": 38, "成功率": 0.94},
                    "外科的治療": {"症例数": 5, "成功率": 0.88},
                    "内科的治療": {"症例数": 2, "成功率": 0.85}
                },
                "合併症率": 0.08,
                "30日死亡率": 0.04,
                "再入院率": 0.06
            },
            "脳梗塞": {
                "年間症例数": 62,
                "年齢別": {
                    "60代": {"症例数": 14, "入院日数平均": 18.5, "治療成功率": 0.87},
                    "70代": {"症例数": 28, "入院日数平均": 22.3, "治療成功率": 0.83},
                    "80代以上": {"症例数": 20, "入院日数平均": 26.1, "治療成功率": 0.79}
                },
                "重症度別": {
                    "軽症": {"症例数": 25, "平均在院日数": 14.2},
                    "中等症": {"症例数": 28, "平均在院日数": 24.6},
                    "重症": {"症例数": 9, "平均在院日数": 38.4}
                }
            },
            "大腿骨骨折": {
                "年間症例数": 78,
                "年齢別": {
                    "70代": {"症例数": 32, "手術成功率": 0.96, "歩行回復率": 0.82},
                    "80代以上": {"症例数": 46, "手術成功率": 0.93, "歩行回復率": 0.74}
                },
                "平均手術待機日数": 2.3,
                "平均在院日数": 28.5
            }
        }
    
    def _add_ehr_integration_note(self, response: str) -> str:
        """電子カルテ連携前提機能の注釈を追加"""
        note = """
        
⚠️ **この機能は電子カルテシステムとの連携が前提の回答です。**
📋 実装時には以下が必要: 
• 電子カルテAPI連携
• DPCデータベース連携
• 診療科別症例登録システム
• 治療成績評価システム
• 医療安全管理システム連携"""
        
        return response + note
    
    def analyze_treatment_outcomes(self, query: str) -> str:
        """治療成績分析"""
        
        # 質問から疾患と年代を抽出
        disease = None
        age_group = None
        
        if "心筋梗塞" in query:
            disease = "急性心筋梗塞"
        elif "脳梗塞" in query:
            disease = "脳梗塞"
        elif "骨折" in query or "大腿骨" in query:
            disease = "大腿骨骨折"
            
        if "60代" in query or "60歳代" in query:
            age_group = "60代"
        elif "70代" in query or "70歳代" in query:
            age_group = "70代"
        elif "80代" in query or "80歳代" in query or "80歳以上" in query:
            age_group = "80代以上"
        elif "50代" in query or "50歳代" in query:
            age_group = "50代"
            
        # 該当データの抽出
        analysis_data = {}
        if disease and disease in self.clinical_data:
            disease_data = self.clinical_data[disease]
            analysis_data[disease] = disease_data
            
            # 年齢群が指定されていればその詳細も追加
            if age_group and age_group in disease_data.get("年齢別", {}):
                analysis_data["指定年齢群詳細"] = disease_data["年齢別"][age_group]
        
        # 全疾患の概要（疾患が特定できない場合）
        if not disease:
            analysis_data = {
                "全疾患概要": {
                    "急性心筋梗塞": f"年間{self.clinical_data['急性心筋梗塞']['年間症例数']}例",
                    "脳梗塞": f"年間{self.clinical_data['脳梗塞']['年間症例数']}例", 
                    "大腿骨骨折": f"年間{self.clinical_data['大腿骨骨折']['年間症例数']}例"
                }
            }
        
        prompt = f"""
        あなたはA病院の医療統計分析担当者です。以下の診療実績データを基に、治療成績について分析・報告してください。
        
        # 分析対象データ
        {analysis_data}
        
        # 質問
        {query}
        
        # 回答形式
        1. **該当症例の概要**: 症例数と基本統計
        2. **治療成績**: 成功率、合併症率、死亡率等の主要指標
        3. **ベンチマーク比較**: 全国平均・地域平均との比較（推定値）
        4. **課題と改善点**: 成績向上のための具体的提案
        5. **今後の取り組み**: 医療の質向上に向けた行動計画
        
        医療の質向上と患者安全に資する実用的な分析を行ってください。
        数値は実際の臨床現場で活用できるよう具体的に示してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"治療成績分析中にエラーが発生しました: {e}"
    
    def analyze_case_statistics(self, query: str) -> str:
        """症例統計分析"""
        
        # 月別症例数の模擬データ生成
        monthly_cases = {}
        for i in range(12):
            month = f"2024-{(i+1):02d}"
            monthly_cases[month] = {
                "急性心筋梗塞": random.randint(2, 6),
                "脳梗塞": random.randint(3, 8),
                "大腿骨骨折": random.randint(4, 10)
            }
        
        prompt = f"""
        あなたはA病院の診療統計担当者です。以下のデータを基に、症例統計について分析してください。
        
        # 年間症例統計
        {self.clinical_data}
        
        # 月別症例推移（直近12ヶ月）
        {monthly_cases}
        
        # 質問
        {query}
        
        # 回答形式
        1. **症例数動向**: 主要疾患の症例数と推移
        2. **季節性分析**: 月別・季節別の特徴
        3. **診療負荷**: 病床稼働への影響と医師負荷
        4. **地域医療への貢献**: 医療圏内での役割
        5. **診療体制強化**: 症例数増加への対応策
        
        地域の中核病院としての役割を踏まえた実践的な分析を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_ehr_integration_note(response.content)
        except Exception as e:
            return f"症例統計分析中にエラーが発生しました: {e}"
    
    def query_clinical_analysis(self, query: str) -> str:
        """診療分析のメインエントリーポイント"""
        query_lower = query.lower()
        
        # キーワードによる機能振り分け
        if any(keyword in query_lower for keyword in ["治療成績", "成功率", "死亡率", "合併症", "治療結果"]):
            return self.analyze_treatment_outcomes(query)
        elif any(keyword in query_lower for keyword in ["症例数", "統計", "推移", "動向"]):
            return self.analyze_case_statistics(query)
        else:
            # デフォルトは治療成績分析
            return self.analyze_treatment_outcomes(query)
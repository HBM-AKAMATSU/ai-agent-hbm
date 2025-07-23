# src/services/enhanced_double_check.py
"""
A病院患者固有データベース対応のダブルチェックサービス
A2024-XXXX形式の患者IDに対応し、実際の処方薬・検査値を考慮した相互作用チェック
"""

import json
import os
import re
from langchain_openai import ChatOpenAI
from config import Config
from datetime import datetime

class EnhancedDoubleCheckService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.detailed_patients = self._load_detailed_patients()
        self.hospital_protocols = self._load_hospital_protocols()
        self.hospital_info = self._load_hospital_info()
        
    def _load_detailed_patients(self):
        """詳細患者データの読み込み"""
        try:
            with open("src/data/dummy_data/detailed_patients.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # 患者IDをキーとした辞書に変換
                patients_dict = {}
                for patient in data.get("patients", []):
                    patients_dict[patient["patient_id"]] = patient
                return patients_dict
        except FileNotFoundError:
            return {}
    
    def _load_hospital_protocols(self):
        """A病院プロトコルの読み込み"""
        try:
            with open("src/data/dummy_data/hospital_protocols.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_hospital_info(self):
        """A病院基本情報の読み込み"""
        try:
            with open("src/data/dummy_data/hospital_info.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"name": "A病院"}
    
    def _extract_patient_and_medication(self, text: str):
        """患者IDと薬剤情報を抽出"""
        # A2024-XXXX形式の患者ID抽出
        patient_match = re.search(r'A2024-\d{4}', text)
        patient_id = patient_match.group(0) if patient_match else None
        
        # 薬剤名と用量の抽出
        medication = None
        dosage = None
        
        # 一般的な薬剤パターン
        drug_patterns = [
            (r"ワーファリン|ワルファリン", "ワーファリン"),
            (r"アスピリン", "アスピリン"),
            (r"クロピドグレル", "クロピドグレル"),
            (r"アピキサバン", "アピキサバン"),
            (r"リバーロキサバン", "リバーロキサバン"),
            (r"メトホルミン|メトグルコ", "メトホルミン"),
            (r"アムロジピン", "アムロジピン"),
            (r"リシノプリル", "リシノプリル"),
            (r"アトルバスタチン", "アトルバスタチン")
        ]
        
        for pattern, drug_name in drug_patterns:
            if re.search(pattern, text):
                medication = drug_name
                break
        
        # 用量抽出
        dosage_match = re.search(r'(\d+(?:\.\d+)?)\s*mg', text)
        if dosage_match:
            dosage = f"{dosage_match.group(1)}mg"
        
        return patient_id, medication, dosage
    
    def check_medication_safety(self, query: str) -> str:
        """A病院患者固有データを用いた薬剤安全性チェック"""
        patient_id, medication, dosage = self._extract_patient_and_medication(query)
        
        if not patient_id:
            return self._provide_general_guidance(query)
        
        if patient_id not in self.detailed_patients:
            return f"""
❌ **A病院患者データベース検索結果**

患者ID「{patient_id}」がA病院のシステムに見つかりません。

📋 **確認事項**
• 患者IDの入力間違いがないか確認してください
• A2024-XXXX形式で正しく入力されているか確認
• 患者が当院に登録済みか確認

💡 **対応方法**
• 正しい患者IDを再入力してください
• 電子カルテで患者登録状況を確認してください
• 医事課にお問い合わせください（内線2001）

---
**A病院 薬剤安全管理システム**
"""
        
        patient_info = self.detailed_patients[patient_id]
        return self._perform_detailed_safety_check(patient_info, medication, dosage, query)
    
    def _perform_detailed_safety_check(self, patient_info, medication, dosage, original_query):
        """詳細な安全性チェック実行"""
        
        # A病院プロトコルに基づく相互作用チェック
        protocol_warnings = self._check_hospital_protocols(patient_info, medication)
        
        # 患者固有リスクファクター
        risk_factors = self._assess_patient_risks(patient_info, medication)
        
        prompt = f"""
        あなたはA病院の薬剤安全管理責任者です。以下の患者データとA病院プロトコルに基づき、処方薬の安全性について評価してください。
        **「🏥 A病院 薬剤安全性評価結果」のようなレポートタイトルや番号付きセクションヘッダー（例:「1. 相互作用評価」）は、回答に含めないでください。**
        質問（「{original_query}」）に直接、自然な会話のような文章で回答してください。
        重要な評価結果、推奨事項、モニタリング指針は、簡潔な文章または必要な場合のみ箇条書きで分かりやすく説明してください。
        回答の冒頭には、必ず患者さんの氏名「{patient_info.get('name', patient_info['patient_id'])}」を含めてください。

        # A病院患者情報
        **患者ID**: {patient_info['patient_id']}
        **年齢・性別**: {patient_info['age']}歳 {patient_info['gender']}
        **主診断**: {patient_info['primary_diagnosis']}
        **既往歴**: {', '.join(patient_info.get('medical_history', []))}
        **アレルギー歴**: {', '.join(patient_info.get('allergies', []))}
        **現在の処方薬**: {', '.join(patient_info.get('current_medications', []))}
        **診療科**: {patient_info['admission_info']['診療科']}
        **主治医**: {patient_info['admission_info']['主治医']}

        # 処方予定薬剤
        **薬剤**: {medication}
        **用量**: {dosage}

        # A病院プロトコル警告
        {protocol_warnings}

        # 患者固有リスクファクター
        {risk_factors}

        # 検査値（関連項目）
        **腎機能**: eGFR {patient_info['lab_values'].get('eGFR', 'N/A')}
        **肝機能**: AST {patient_info['lab_values'].get('AST', 'N/A')}, ALT {patient_info['lab_values'].get('ALT', 'N/A')}
        **凝固機能**: PT-INR {patient_info['lab_values'].get('PT-INR', 'N/A')}

        実際のA病院診療に基づく具体的で実用的な安全性評価を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"A病院薬剤安全性チェック中にエラーが発生しました: {e}"
    
    def _check_hospital_protocols(self, patient_info, medication):
        """A病院プロトコルに基づく警告生成"""
        warnings = []
        
        if medication == "ワーファリン" and "anticoagulation_protocol" in self.hospital_protocols:
            protocol = self.hospital_protocols["anticoagulation_protocol"]["warfarin_initiation"]
            
            # 年齢に基づく用量チェック
            if patient_info["age"] >= 70:
                warnings.append(f"⚠️ A病院プロトコル: 70歳以上は開始用量1mg/日推奨（現在{patient_info['age']}歳）")
            
            # 併用薬チェック
            current_meds = patient_info.get("current_medications", [])
            for med in current_meds:
                if "アスピリン" in med or "NSAID" in med:
                    warnings.append("⚠️ A病院プロトコル: NSAID併用時は消化管出血リスク評価必須")
        
        return "\n".join(warnings) if warnings else "プロトコル上の特記事項なし"
    
    def _assess_patient_risks(self, patient_info, medication):
        """患者固有リスク評価"""
        risks = []
        
        # 腎機能チェック
        egfr = patient_info['lab_values'].get('eGFR', 100)
        if egfr < 30 and medication in ["メトホルミン"]:
            risks.append(f"🚨 重要: eGFR {egfr} - {medication}は腎機能低下により禁忌")
        
        # 肝機能チェック  
        ast = patient_info['lab_values'].get('AST', 30)
        alt = patient_info['lab_values'].get('ALT', 30)
        if (ast > 100 or alt > 100) and "スタチン" in medication:
            risks.append(f"⚠️ 注意: 肝機能異常あり（AST:{ast}, ALT:{alt}） - {medication}慎重投与")
        
        # アレルギーチェック
        allergies = patient_info.get("allergies", [])
        if medication == "アスピリン" and "NSAIDs" in allergies:
            risks.append("🚨 アレルギー警告: NSAIDsアレルギー歴あり - アスピリン投与注意")
        
        return "\n".join(risks) if risks else "患者固有の特記リスクなし"
    
    def _provide_general_guidance(self, query):
        """一般的なガイダンス提供"""
        return f"""
🏥 **A病院 薬剤安全管理システム**

患者IDが特定できませんでした。A病院での安全な処方のため、以下の手順で再度お試しください：

📋 **正しい使用方法**
• 患者ID: A2024-XXXX形式で入力してください
• 例: 「患者A2024-0156にワーファリン2mg処方したい。相互作用は？」

⚕️ **A病院の薬剤安全管理**
• 全処方薬は当院独自プロトコルでチェック
• 患者固有データ（アレルギー、併用薬、検査値）を総合評価
• 24時間薬剤師オンコール体制（内線3001）

💡 **緊急時対応**
緊急の薬剤相談は薬剤部直通（内線3001）または当直薬剤師まで

---
入力された質問: {query}
"""
    
    def query_medication_check(self, query: str) -> str:
        """メインエントリーポイント"""
        return self.check_medication_safety(query)
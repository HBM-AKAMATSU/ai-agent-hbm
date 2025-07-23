# src/services/double_check.py (OpenAI版)
import json
import re
from langchain_openai import ChatOpenAI
from config import Config

class DoubleCheckService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.patient_data = self._load_patient_data()

    def _load_patient_data(self):
        try:
            with open("src/data/dummy_data/patients.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"patients": []}

    def _extract_info(self, text: str):
        # P-XXX形式とA2024-XXXX形式の両方に対応
        patient_id_match = re.search(r'([P|p]-\d{3}|A2024-\d{4})', text)
        patient_id = patient_id_match.group(0).upper() if patient_id_match else None
        medication = None
        if "ワーファリン" in text or "ワルファリン" in text: medication = "ワーファリン"
        elif "ロセフィン" in text or "セフトリアキソン" in text: medication = "セフトリアキソン"
        elif "メトグルコ" in text or "メトホルミン" in text: medication = "メトホルミン"
        elif "造影剤" in text or "CT造影剤" in text: medication = "造影剤"
        return patient_id, medication

    def check_medication(self, text: str) -> str:
        patient_id, medication = self._extract_info(text)
        if not patient_id or not medication:
            return "患者IDまたは薬剤名を認識できませんでした。"
        
        # A2024形式の場合はdetailed_patients.jsonから取得
        if patient_id.startswith("A2024"):
            try:
                with open("src/data/dummy_data/detailed_patients.json", "r", encoding="utf-8") as f:
                    detailed_data = json.load(f)
                patient_info = next((p for p in detailed_data.get("patients", []) if p.get("patient_id") == patient_id), None)
            except FileNotFoundError:
                return "患者データベースにアクセスできませんでした。"
        else:
            # P-XXX形式の場合は従来のpatients.jsonから取得
            patient_info = next((p for p in self.patient_data.get("patients", []) if p["id"] == patient_id), None)
        
        if not patient_info:
            return f"患者ID {patient_id} の情報が見つかりません。"
        
        # A2024形式とP-XXX形式でデータ構造が異なるため調整
        if patient_id.startswith("A2024"):
            patient_display_id = patient_info.get('patient_id', patient_id)
            allergies = ', '.join(patient_info.get('allergies', []))
            current_medications = ', '.join(patient_info.get('current_medications', []))
            conditions = ', '.join(patient_info.get('medical_history', []))
        else:
            patient_display_id = patient_info.get('id', patient_id)
            allergies = ', '.join(patient_info.get('allergies', []))
            current_medications = ', '.join(patient_info.get('current_medications', []))
            conditions = ', '.join(patient_info.get('conditions', []))
        
        # 造影剤の場合とその他の薬剤で指示を分ける
        if medication == "造影剤":
            prompt_instructions = """
            あなたは医療安全を担当する薬剤師です。以下の患者情報と、使用予定の造影剤に関する情報に基づき、特に**アレルギー歴**に焦点を当てて安全性評価を行い、リスクがあれば具体的に警告してください。
            """
            usage_text = "使用予定"
            check_items = f"""
        1. アレルギー歴と使用予定の{medication}は問題ないか？ (特にアレルギー歴を重視)
        2. 現在の服用薬との間に重大な相互作用はないか？
        3. 既往歴に対して使用予定の{medication}は禁忌または慎重投与に該当しないか？"""
        else:
            prompt_instructions = """
            あなたは医療安全を担当する薬剤師です。以下の情報を基に、投薬の安全性について評価し、リスクがあれば具体的に警告してください。
            """
            usage_text = "処方予定"
            check_items = f"""
        1. アレルギー歴と処方薬は問題ないか？
        2. 現在の服用薬との間に重大な相互作用はないか？
        3. 既往歴に対して処方薬は禁忌または慎重投与に該当しないか？"""
            
        prompt = f"""
        {prompt_instructions}
        # 患者情報
        - ID: {patient_display_id}
        - 氏名: {patient_info.get('name')}
        - アレルギー歴: {allergies}
        - 現在の服用薬: {current_medications}
        - 既往歴: {conditions}
        # 処方/使用指示
        {medication}を{usage_text}です。
        # チェック項目{check_items}
        # 回答形式
        リスクが一つでもあれば「⚠️【AI簡易ダブルチェック結果】」から始めて、具体的なリスク内容を箇条書きで指摘してください。
        リスクがなければ「✅【AI簡易ダブルチェック結果】特記すべき問題は見つかりませんでした。」とだけ回答してください。
        回答の冒頭には、**必ず患者さんの氏名を含めてください。** 例：「患者名: [患者氏名]様の安全評価結果...」
        """
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"ダブルチェック中にエラーが発生しました: {e}")
            return "申し訳ありません、ダブルチェックを実行できませんでした。"
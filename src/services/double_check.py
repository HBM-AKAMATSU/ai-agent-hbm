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
        patient_id_match = re.search(r'[P|p]-\d{3}', text)
        patient_id = patient_id_match.group(0).upper() if patient_id_match else None
        medication = None
        if "ワーファリン" in text or "ワルファリン" in text: medication = "ワーファリン"
        elif "ロセフィン" in text or "セフトリアキソン" in text: medication = "セフトリアキソン"
        elif "メトグルコ" in text or "メトホルミン" in text: medication = "メトホルミン"
        return patient_id, medication

    def check_medication(self, text: str) -> str:
        patient_id, medication = self._extract_info(text)
        if not patient_id or not medication:
            return "患者IDまたは薬剤名を認識できませんでした。"
        patient_info = next((p for p in self.patient_data.get("patients", []) if p["id"] == patient_id), None)
        if not patient_info:
            return f"患者ID {patient_id} の情報が見つかりません。"
        
        prompt = f"""
        あなたは医療安全を担当する薬剤師です。以下の情報を基に、投薬の安全性について評価し、リスクがあれば具体的に警告してください。
        # 患者情報
        - ID: {patient_info.get('id')}
        - 氏名: {patient_info.get('name')}
        - アレルギー歴: {', '.join(patient_info.get('allergies', []))}
        - 現在の服用薬: {', '.join(patient_info.get('current_medications', []))}
        - 既往歴: {', '.join(patient_info.get('conditions', []))}
        # 処方指示
        {medication}を処方予定です。
        # チェック項目
        1. アレルギー歴と処方薬は問題ないか？
        2. 現在の服用薬との間に重大な相互作用はないか？
        3. 既往歴に対して処方薬は禁忌または慎重投与に該当しないか？
        # 回答形式
        リスクが一つでもあれば「⚠️【AI簡易ダブルチェック結果】」から始めて、具体的なリスク内容を箇条書きで指摘してください。
        リスクがなければ「✅【AI簡易ダブルチェック結果】特記すべき問題は見つかりませんでした。」とだけ回答してください。
        """
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"ダブルチェック中にエラーが発生しました: {e}")
            return "申し訳ありません、ダブルチェックを実行できませんでした。"
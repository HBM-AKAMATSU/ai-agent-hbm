# src/services/router.py (OpenAI版)
from langchain_openai import ChatOpenAI
from config import Config

class QuestionRouter:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )

    def classify_question(self, question: str) -> str:
        prompt = f"""
        あなたは病院内の優秀なアシスタントです。職員からの以下の質問を、最も適切なカテゴリに一つだけ分類してください。

        # カテゴリ定義
        - 'admin': 院内規定、経費精算、福利厚生、勤怠、担当者の問い合わせなど、事務・総務に関する質問。
        - 'medical': 薬剤の用法・用量、副作用、相互作用など、医薬品や医療行為に関する専門的な質問。
        - 'double_check': 「チェックして」「確認お願いします」といった、投薬前の安全確認を直接依頼する内容。
        - 'task': 「議事録をまとめて」「保存して」など、具体的な作業を依頼する内容。
        - 'unknown': 上記のいずれにも当てはまらない、または分類が困難な場合。

        # 質問文
        "{question}"

        # 出力形式
        分類結果のカテゴリ名（例: admin, medical, double_check, task, unknown）のみを、小文字の英単語で回答してください。
        """
        try:
            response = self.model.invoke(prompt)
            return response.content.strip().replace("`", "").lower()
        except Exception as e:
            print(f"Error in question classification: {e}")
            return "unknown"
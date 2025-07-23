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
        # 最優先：患者IDが含まれ、かつ薬剤チェック関連の場合のみdouble_checkに分類
        if self._contains_patient_id(question) and self._is_medication_check(question):
            return "double_check"
        
        prompt = f"""
        あなたは病院内の優秀なアシスタントです。職員からの以下の質問を、最も適切なカテゴリに一つだけ分類してください。

        # カテゴリ定義
        ## 基本機能
        - 'admin': 院内規定、経費精算、福利厚生、勤怠、担当者の問い合わせなど、一般的な事務・総務に関する質問。
        - 'medical': 薬剤の用法・用量、副作用、相互作用など、医薬品や医療行為に関する専門的な質問（患者固有でない一般的な質問）。
        - 'double_check': 「チェックして」「確認お願いします」といった、投薬前の安全確認を直接依頼する内容。
        - 'patient_info_query': 「名前は？」「生年月日は？」「住所は？」など、特定の患者ID（例: P-XXX, A2024-XXXX）を指定して、その患者の基本情報を問い合わせる内容。
        - 'task': 「議事録をまとめて」「保存して」など、具体的な作業を依頼する内容。
        
        ## 医療事務向け高度分析機能
        - 'billing_analysis': 診療報酬、査定、収益分析、競合比較など、診療報酬に関する分析要求。
        - 'bed_management': 病床稼働率、在院日数、退院調整など、病床管理に関する分析要求。
        - 'admin_efficiency': スタッフ生産性、エラー率、研修効果など、事務業務効率化に関する分析要求。
        - 'revenue_analysis': 収益構造、経営指標、KPI分析など、経営分析に関する質問。
        - 'clinical_analysis': 治療成績、症例統計、疾患別分析、論文研究支援など、診療実績に関する質問。
        - 'waiting_analysis': 待ち時間、患者動線、満足度分析など、患者サービス向上に関する分析要求。
        - 'staff_training': 職員研修、研修効果、職員教育、人材育成に関する質問。
        - 'summary': 前回の回答の要約、まとめ、総括を求める質問。「一言で」「短く」「簡潔に」「ポイントは」など、情報を集約・簡略化する依頼。
        - 'feedback': 「ありがとう」「助かります」「いい感じですね」「すごい」「よかった」「なるほど」など、システムや回答に対する肯定的な評価、感想、感謝、相槌を表す内容。
        - 'general_chat': 「普通に会話はできますか？」「元気？」「こんにちは」「今日の気分は？」など、システムとの一般的な対話や雑談、日常的な挨拶に関する内容。
        - 'shift_scheduling': 「シフト組んで」「シフト希望」「勤務表作成」など、シフトや勤務表の作成、希望提出に関する内容。
        
        - 'unknown': 上記のいずれにも当てはまらない、または分類が困難な場合。

        # 質問文
        "{question}"

        # 分類のヒント
        - 「査定」「減点」「返戻」「診療報酬」「請求」→ billing_analysis
        - 「病床」「稼働率」「在院日数」「ベッド」「入院」「退院」→ bed_management  
        - 「スタッフ」「効率」「エラー率」「生産性」「研修」→ admin_efficiency
        - 「収益」「売上」「経営」「利益」「コスト」→ revenue_analysis
        - 「治療成績」「実績」「症例数」「死亡率」「成功率」「合併症」「論文」「研究」「データ分析」→ clinical_analysis
        - 「待ち時間」「患者満足度」「患者動線」→ waiting_analysis
        - 「研修」「職員」「教育」「人材育成」「研修効果」「報告書」→ staff_training
        - 「名前は」「氏名は」「患者情報」「基本情報」「生年月日」「住所」→ patient_info_query
        - 「要約」「まとめ」「総括」「簡潔に」「ポイントは」「結論は」「一言で」「短く」「概要」→ summary
        - 「ありがとう」「助かります」「いい感じ」「すごい」「よかった」「なるほど」「素晴らしい」「完璧」「感謝」→ feedback
        - 「普通に会話」「雑談」「元気」「こんにちは」「おはよう」「こんばんは」「気分」「天気」「今日」→ general_chat
        - 「シフト」「勤務表」「希望日」「組んで」「シフト作成」「スケジュール」→ shift_scheduling
        
        # 重要な分類指針:
        - 論文・研究・データ分析に関する質問は clinical_analysis に分類する
        - 「一言で」「短く」「まとめ」「要約」など情報集約の依頼は summary に分類する
        - **「ありがとう」「いい感じ」「助かる」「すごい」「感謝」など肯定的な感想や相槌は必ず feedback に分類する**
        - **feedback の判定は最優先：他のカテゴリより優先して feedback を選択する**
        - 短い感謝や評価の言葉は具体的な質問がない限り必ず feedback として扱う
        - 会話履歴があっても、感謝・評価・相槌の意図が明確な場合は feedback を選択する

        # 出力形式
        分類結果のカテゴリ名のみを、小文字の英単語で回答してください。
        """
        try:
            response = self.model.invoke(prompt)
            return response.content.strip().replace("`", "").lower()
        except Exception as e:
            print(f"Error in question classification: {e}")
            return "unknown"
    
    def _contains_patient_id(self, question: str) -> bool:
        """患者IDの存在を確認"""
        import re
        # A2024-XXXX形式のパターンチェック
        pattern = r'A2024-\d{4}'
        return bool(re.search(pattern, question))
    
    def _is_medication_check(self, question: str) -> bool:
        """薬剤チェック関連の質問かどうかを確認"""
        medication_keywords = [
            "チェック", "確認", "処方", "投薬", "薬", "相互作用", "副作用", 
            "ワーファリン", "ワルファリン", "ロセフィン", "セフトリアキソン", 
            "メトグルコ", "メトホルミン", "大丈夫", "安全"
        ]
        return any(keyword in question for keyword in medication_keywords)
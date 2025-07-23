# src/services/rag_service.py (OpenAI版 - import修正)
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from config import Config

class RAGService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.admin_vectorstore = None
        self.medical_vectorstore = None
    
    # setup_vectorstoresは以前の「読み込み専用」のままでOKです
    def setup_vectorstores(self):
        """保存されたベクトルデータベースを読み込む"""
        print("保存されたベクトルデータベースを読み込みます...")
        try:
            if os.path.exists("faiss_index_admin"):
                self.admin_vectorstore = FAISS.load_local(
                    "faiss_index_admin", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("事務規定データベースの読み込み完了。")
            else:
                print("警告: 保存された事務DB 'faiss_index_admin' が見つかりません。")

            if os.path.exists("faiss_index_medical"):
                self.medical_vectorstore = FAISS.load_local(
                    "faiss_index_medical", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("医薬品情報データベースの読み込み完了。")
            else:
                print("警告: 保存された医療DB 'faiss_index_medical' が見つかりません。")
        except Exception as e:
            print(f"データベースの読み込み中にエラーが発生しました: {e}")

    def _generate_response(self, question: str, vectorstore, prompt_template: str) -> str:
        if not vectorstore:
            return "申し訳ありません、関連するデータベースが初期化されていません。"
        
        docs = vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=question)
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"回答生成中にエラーが発生しました: {e}")
            return "申し訳ありません、回答を生成できませんでした。"

    def query_admin(self, question: str) -> str:
        prompt_template = """
        あなたはA病院の事務規定に詳しいアシスタントです。以下の参考文書を基に、質問に対する**最も重要な事実と数値を抽出し、箇条書きで簡潔に**記述してください。
        **余計な前置き、ヘッダー、タイトル、番号付け、複雑な文章構造、テーブル形式は一切含めないでください。**
        質問に直接関連する事実のみを抽出してください。
        # 参考文書:
        {context}
        # 質問:
        {question}
        # 回答:
        """
        return self._generate_response(question, self.admin_vectorstore, prompt_template)

    def query_medical(self, question: str) -> str:
        if not self.medical_vectorstore:
            # Enhanced medical response without vectorstore
            return self._generate_enhanced_medical_response(question)
            
        prompt_template = """
        あなたはA病院の薬剤情報に精通した医療専門家です。以下の医薬品情報（またはその他の医療関連情報）を基に、質問に対する**最も重要な事実と数値を抽出し、箇条書きで簡潔に**記述してください。
        **余計な前置き、ヘッダー、タイトル、番号付け、複雑な文章構造、テーブル形式は一切含めないでください。**
        質問に直接関連する事実のみを抽出してください。
        # 参考文書:
        {context}
        # 質問:
        {question}
        # 回答:
        """
        return self._generate_response(question, self.medical_vectorstore, prompt_template)
    
    def _generate_enhanced_medical_response(self, question: str) -> str:
        """ベクトルデータベースなしでのA病院固有医療回答"""
        prompt = f"""
        あなたはA病院の薬剤安全管理責任者です。A病院の実績と安全管理基準に基づき、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # A病院の薬剤安全管理体制
        - 24時間薬剤師オンコール体制（内線3001）
        - 電子処方箋システム導入済み
        - 薬剤相互作用チェック機能完備
        - 患者固有データベース（A2024-XXXX形式）

        # A病院のメトホルミン安全使用基準
        - eGFR 30未満は投与禁忌
        - eGFR 30-45は慎重投与（定期腎機能監視）
        - 造影剤使用時は一時休薬
        - 手術前48時間は休薬
        - 重篤感染症・脱水時は休薬

        # A病院での腎機能評価基準
        - 65歳以上は3ヶ月毎腎機能検査
        - CKD stage 3b以上は専門医連携
        - 薬剤性腎障害モニタリング実施

        # 質問
        {question}

        # 回答
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"A病院薬剤安全管理システムでエラーが発生しました: {e}"
    
    def summarize_previous_response(self, conversation_history: str, current_question: str) -> str:
        """前回の回答を要約する機能"""
        prompt = f"""
        あなたはA病院の情報整理専門スタッフです。前回までの相談内容を効率的に要約してください。

        # 相談履歴の詳細
        {conversation_history}

        # 要約の依頼内容
        {current_question}

        # 要約作成の基準
        1. **優先順位**: 患者安全→診療品質→業務効率→コスト
        2. **A病院固有情報**: 実績数値、プロトコル、特色を重視
        3. **実務活用性**: 明日から使える具体的情報を抽出
        4. **継続性**: 次回相談で参照しやすい構成

        # 要約構成テンプレート
        📋 **A病院 相談要約レポート**

        ## 🎯 **相談の要点**
        1. **主要テーマ**: [メインの相談内容]
        2. **A病院での実績**: [当院固有の数値・実績]
        3. **重要な結論**: [意思決定に影響する要点]

        ## 📊 **A病院データサマリー**
        - **症例数/実績**: [具体的数値]
        - **治療成績**: [成功率、合併症率等]
        - **当院の特色**: [他院との差別化要因]

        ## 🔄 **次回への継続事項**
        - **フォローアップ項目**: [追加検討すべき点]
        - **参考資料**: [関連ガイドライン、プロトコル]

        ## 💼 **実務活用ポイント**
        - [即座に実践できる具体的な活用方法]

        実務担当者が効率的に参照できる構成で要約してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"要約生成中にエラーが発生しました: {e}"
    
    def query_admin_with_history(self, question: str, conversation_history: str = "") -> str:
        """会話履歴を考慮した事務規定回答"""
        prompt_template = """
        あなたはA病院の事務規定に詳しいアシスタントです。以下の情報を総合的に考慮し、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # 会話の流れとコンテキスト
        {history}

        # A病院の関連規定・文書
        {context}
        
        # 現在のご質問
        {question}
        
        # 回答指針
        - 前回の会話内容との関連性を自然に織り込む
        - A病院固有の規定を要点として抽出
        - 具体的な手続きや連絡先を含める
        - 必要に応じてフォローアップを提案
        
        # 回答
        """
        
        if not self.admin_vectorstore:
            return "申し訳ありません、事務規定データベースが初期化されていません。"
        
        docs = self.admin_vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=question, history=conversation_history)
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
    
    def query_medical_with_history(self, question: str, conversation_history: str = "") -> str:
        """会話履歴を考慮した医療回答"""
        if not self.medical_vectorstore:
            return self._generate_enhanced_medical_response_with_history(question, conversation_history)
            
        prompt_template = """
        あなたはA病院の薬剤安全管理責任者です。継続的な相談として以下の情報を総合的に評価し、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # これまでの相談経緯
        {history}

        # A病院の薬剤安全管理データベース
        {context}
        
        # 現在のご相談
        {question}
        
        # 安全管理指針
        - 前回の相談内容との関連性を自然に織り込む
        - A病院の安全使用基準に基づく評価要点を抽出
        - 患者固有リスクの継続的評価ポイント
        - 必要に応じて追加検査・モニタリングを提案
        
        # 回答
        """
        
        docs = self.medical_vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=question, history=conversation_history)
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
    
    def _generate_enhanced_medical_response_with_history(self, question: str, conversation_history: str) -> str:
        """会話履歴を考慮したA病院固有医療回答"""
        prompt = f"""
        あなたはA病院の薬剤安全管理責任者です。前回までの会話を踏まえ、A病院の実績と安全管理基準に基づき、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # 前回までの会話履歴
        {conversation_history}

        # A病院の薬剤安全管理体制
        - 24時間薬剤師オンコール体制（内線3001）
        - 電子処方箋システム導入済み
        - 薬剤相互作用チェック機能完備
        - 患者固有データベース（A2024-XXXX形式）

        # A病院のメトホルミン安全使用基準
        - eGFR 30未満は投与禁忌
        - eGFR 30-45は慎重投与（定期腎機能監視）
        - 造影剤使用時は一時休薬
        - 手術前48時間は休薬
        - 重篤感染症・脱水時は休薬

        # A病院での腎機能評価基準
        - 65歳以上は3ヶ月毎腎機能検査
        - CKD stage 3b以上は専門医連携
        - 薬剤性腎障害モニタリング実施

        # 質問
        {question}

        # 回答
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"A病院薬剤安全管理システムでエラーが発生しました: {e}"
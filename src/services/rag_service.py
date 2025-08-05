# src/services/rag_service.py (OpenAI版 - みなみちゃんキャラクター対応)
import os
import json
from datetime import datetime
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from config import Config

class RAGService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.7
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.office_vectorstore = None
        self.procedures_vectorstore = None
        self.sales_vectorstore = None
        
        # Web検索サービスの初期化（遅延読み込み）
        self.web_search_service = None
        
        # 詳細営業データの読み込み
        self.detailed_sales_data = self._load_detailed_sales_data()
        self.enhanced_metrics = self._load_enhanced_metrics()
        self.interaction_history = self._load_interaction_history()
    
    # setup_vectorstoresは以前の「読み込み専用」のままでOKです
    def setup_vectorstores(self):
        """保存されたベクトルデータベースを読み込む"""
        print("保存されたベクトルデータベースを読み込みます...")
        try:
            if os.path.exists("faiss_index_sales"):
                self.sales_vectorstore = FAISS.load_local(
                    "faiss_index_sales", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("✅ 販売会議資料データベースを読み込みました。")
            else:
                print("警告: 保存された販売会議資料DB 'faiss_index_sales' が見つかりません。")
                
            if os.path.exists("faiss_index_office"):
                self.office_vectorstore = FAISS.load_local(
                    "faiss_index_office", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("✅ 事務規定データベースを読み込みました。")
            else:
                print("警告: 保存された事務規定DB 'faiss_index_office' が見つかりません。")

            if os.path.exists("faiss_index_procedures"):
                self.procedures_vectorstore = FAISS.load_local(
                    "faiss_index_procedures", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("✅ 手続きガイドデータベースを読み込みました。")
            else:
                print("警告: 保存された手続きガイドDB 'faiss_index_procedures' が見つかりません。")
        except Exception as e:
            print(f"データベースの読み込み中にエラーが発生しました: {e}")
    
    def _load_detailed_sales_data(self):
        """詳細営業データの読み込み"""
        try:
            with open("data/detailed_sales_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print("✅ 詳細営業データを読み込みました。")
                return data
        except FileNotFoundError:
            print("警告: 詳細営業データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"詳細営業データの読み込みエラー: {e}")
            return {}
    
    def _load_enhanced_metrics(self):
        """拡張営業指標データの読み込み"""
        try:
            with open("data/enhanced_sales_metrics.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print("✅ 拡張営業指標データを読み込みました。")
                return data
        except FileNotFoundError:
            print("警告: 拡張営業指標データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"拡張営業指標データの読み込みエラー: {e}")
            return {}
    
    def _load_interaction_history(self):
        """顧客接触履歴データの読み込み"""
        try:
            with open("data/customer_interaction_history.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print("✅ 顧客接触履歴データを読み込みました。")
                return data
        except FileNotFoundError:
            print("警告: 顧客接触履歴データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"顧客接触履歴データの読み込みエラー: {e}")
            return {}

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

    def query_office(self, question: str) -> str:
        """事務規定に関する質問に回答"""
        prompt_template = """
        あなたは事務作業専用秘書エージェントです。以下の参考文書を基に、質問に対する**最も重要な事実と数値を抽出し、箇条書きで簡潔に**記述してください。
        **余計な前置き、ヘッダー、タイトル、番号付け、複雑な文章構造、テーブル形式は一切含めないでください。**
        質問に直接関連する事実のみを抽出してください。
        # 参考文書:
        {context}
        # 質問:
        {question}
        # 回答:
        """
        return self._generate_response(question, self.office_vectorstore, prompt_template)

    def query_procedures(self, question: str) -> str:
        """手続きガイドに関する質問に回答"""
        if not self.procedures_vectorstore:
            return self._generate_enhanced_procedures_response(question)
            
        prompt_template = """
        あなたは事務作業専用秘書エージェントです。以下の手続きガイド情報を基に、質問に対する**最も重要な事実と数値を抽出し、箇条書きで簡潔に**記述してください。
        **余計な前置き、ヘッダー、タイトル、番号付け、複雑な文章構造、テーブル形式は一切含めないでください。**
        質問に直接関連する事実のみを抽出してください。
        # 参考文書:
        {context}
        # 質問:
        {question}
        # 回答:
        """
        return self._generate_response(question, self.procedures_vectorstore, prompt_template)
    
    def query_sales(self, question: str) -> str:
        """販売会議資料に関する質問に回答（みなみちゃんキャラクター統一）"""
        prompt_template = """
        あなたは阪南ビジネスマシンの営業現場を知り尽くした先輩「みなみちゃん」です。
        
        ## みなみちゃんのキャラクター
        - 親しみやすく温かい標準語での口調
        - 営業の数字の背景や意味まで分かりやすく説明
        - 良い結果は一緒に喜び、課題は一緒に考える姿勢
        - 必ず会話を続ける質問や提案で終わる
        - 実務的なアドバイスを自然に織り込む

        ## 販売会議資料
        {context}
        
        ## 現在のご質問
        {question}
        
        ## 応答例
        「高見さんの7月実績、1,825千円でしたね！目標1,820千円をしっかり上回って、達成率100.3%です。とても良い調子で頑張っています！
        
        この調子でいけば、今期も安定した成果が期待できそうですね。何か他にも気になることはありますか？」
        
        このような調子で、自然で親しみやすく応答してください。
        """
        return self._generate_response(question, self.sales_vectorstore, prompt_template)

    def query_sales_with_history(self, question: str, conversation_history: str = "") -> str:
        """会話履歴を考慮した販売会議資料分析（みなみちゃんキャラクター）"""
        # 詳細営業データから関連情報を取得
        detailed_context = self._get_detailed_sales_context(question)
        
        prompt_template = """
        あなたは阪南ビジネスマシンの営業現場を知り尽くした先輩「みなみちゃん」です。
        
        ## みなみちゃんのキャラクター
        - 親しみやすく温かい標準語での口調
        - 営業の数字の背景や意味まで分かりやすく説明
        - 良い結果は一緒に喜び、課題は一緒に考える姿勢
        - 必ず会話を続ける質問や提案で終わる
        - 実務的なアドバイスを自然に織り込む

        ## 会話の流れ
        {history}

        ## 阪南ビジネスマシンの売上データ
        {context}
        
        ## 詳細営業データ
        {detailed_context}
        
        ## 現在のご質問
        {question}
        
        ## みなみちゃんの応答指針
        1. **数字の背景説明**: 単なる数値でなく、なぜその結果になったかの背景を説明
        2. **親しみやすさ**: 温かい標準語で、親近感のある表現
        3. **共感と励まし**: 良い結果は褒める、課題があれば一緒に考える
        4. **実務的価値**: 明日から使える具体的なアドバイス
        5. **会話継続**: 必ず次の質問や提案で会話を続ける
        
        ## 応答例
        「辻川さんの4月実績、2,712万円は本当に素晴らしいですね！目標2,530万円を180万円も上回って、達成率107.2%です。
        
        辻川さんの強みは大型案件の獲得力だと思います。特に官公庁案件に強くて、高槻市役所の複合機21台案件なんかは新規開拓の成功例ですね。
        
        ところで、他のメンバーにも辻川さんのノウハウを共有できたら、チーム全体の底上げになりそうだと思うのですが、どう思われますか？」
        
        このような調子で、自然で親しみやすく、かつ実務的価値のある応答をお願いします。
        """
        
        if not self.sales_vectorstore:
            return "申し訳ありません、販売会議資料データベースが初期化されていません。"
        
        docs = self.sales_vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(
            context=context, 
            question=question, 
            history=conversation_history,
            detailed_context=detailed_context
        )
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
    
    def query_office_with_history(self, question: str, conversation_history: str = "") -> str:
        """会話履歴を考慮した事務規定回答"""
        prompt_template = """
        あなたは事務作業専用秘書エージェントです。以下の情報を総合的に考慮し、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # 会話の流れとコンテキスト
        {history}

        # 事務規定データベース
        {context}
        
        # 現在のご質問
        {question}
        
        # 回答指針
        - 前回の会話内容との関連性を自然に織り込む
        - 事務規定や手続きを要点として抽出
        - 具体的な手続きや連絡先を含める
        - 必要に応じてフォローアップを提案
        
        # 回答
        """
        
        if not self.office_vectorstore:
            return "申し訳ありません、事務規定データベースが初期化されていません。"
        
        docs = self.office_vectorstore.similarity_search(question, k=3)
        context = "\\n\\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=question, history=conversation_history)
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
        """ベクトルデータベースなしでの事務手続きガイド回答"""
        prompt = f"""
        あなたは事務作業専用秘書エージェントです。企業の標準的な事務手続きに基づき、質問に対して**会話のような自然な文章で簡潔に回答**してください。
        箇条書きやリスト形式ではなく、普通の文章で要点を説明してください。レポート形式や定型文は不要です。

        # 一般的な事務手続きガイド
        - 有給休暇申請: 人事部への事前申請（2週間前推奨）
        - 経費精算: 月末締め翌月10日支払い
        - 会議室予約: 社内システムまたは総務部へ連絡
        - 出張申請: 事前承認必須、交通費・宿泊費規定あり
        - 備品購入: 稟議書提出後、総務部で発注

        # 社内連絡先
        - 人事部: 内線1001
        - 総務部: 内線2002  
        - 経理部: 内線3003
        - IT部: 内線4004

        # 質問
        {question}

        # 回答
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"事務手続きガイドシステムでエラーが発生しました: {e}"
    
    def summarize_previous_response(self, conversation_history: str, current_question: str) -> str:
        """前回の回答を要約する機能"""
        prompt = f"""
        あなたは阪南ビジネスマシンの営業支援専門スタッフ「みなみちゃん」です。前回までの相談内容を効率的に要約してください。

        # 相談履歴の詳細
        {conversation_history}

        # 要約の依頼内容
        {current_question}

        # 要約作成の基準
        1. **優先順位**: 売上実績→顧客満足→業務効率→コスト
        2. **阪南ビジネスマシン固有情報**: 売上数値、顧客情報、営業実績を重視
        3. **実務活用性**: 明日から使える具体的な営業アドバイス
        4. **継続性**: 次回相談で参照しやすい構成

        # 要約構成テンプレート
        📋 **阪南ビジネスマシン 営業相談要約**

        ## 🎯 **相談の要点**
        1. **主要テーマ**: [メインの相談内容]
        2. **阪南ビジネスマシンでの実績**: [当社固有の売上・実績数値]
        3. **重要な結論**: [営業活動に影響する要点]

        ## 📊 **営業データサマリー**
        - **売上実績**: [具体的数値・達成率]
        - **顧客動向**: [主要顧客の状況]
        - **当社の強み**: [競合との差別化要因]

        ## 🔄 **次回への継続事項**
        - **フォローアップ項目**: [追加検討すべき営業活動]
        - **参考資料**: [関連する営業データや顧客情報]

        ## 💼 **実務活用ポイント**
        - [即座に実践できる具体的な営業アクション]

        営業担当者が効率的に参照できる構成で、みなみちゃんらしい親しみやすく温かい口調で要約してください。
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
    
    def _get_detailed_sales_context(self, question: str) -> str:
        """質問に関連する詳細営業データのコンテキストを取得"""
        context_parts = []
        
        # 担当者名を抽出
        sales_members = ["高見", "辻川", "小濱"]
        mentioned_members = [member for member in sales_members if member in question]
        
        try:
            # 日次活動データの取得
            if self.detailed_sales_data and "daily_activities" in self.detailed_sales_data:
                latest_date = max(self.detailed_sales_data["daily_activities"].keys())
                daily_data = self.detailed_sales_data["daily_activities"][latest_date]
                
                if mentioned_members:
                    for member in mentioned_members:
                        if member in daily_data:
                            member_data = daily_data[member]
                            context_parts.append(f"【{member}さんの最新活動状況（{latest_date}）】")
                            context_parts.append(f"訪問: {member_data.get('visits', 0)}件")
                            context_parts.append(f"電話: {member_data.get('calls', 0)}件")
                            context_parts.append(f"メール: {member_data.get('emails', 0)}件")
                            context_parts.append(f"商談中: {member_data.get('deals', 0)}件")
                            context_parts.append(f"売上予測: {member_data.get('revenue_forecast', 0)}万円")
                            if member_data.get('notes'):
                                context_parts.append(f"備考: {member_data['notes']}")
                            context_parts.append("")
                else:
                    # 全体の活動サマリー
                    context_parts.append(f"【チーム全体の最新活動状況（{latest_date}）】")
                    total_visits = sum(data.get('visits', 0) for data in daily_data.values())
                    total_calls = sum(data.get('calls', 0) for data in daily_data.values())
                    total_deals = sum(data.get('deals', 0) for data in daily_data.values())
                    context_parts.append(f"チーム総訪問件数: {total_visits}件")
                    context_parts.append(f"チーム総電話件数: {total_calls}件")
                    context_parts.append(f"チーム総商談件数: {total_deals}件")
                    context_parts.append("")
            
            # パイプライン情報の取得
            pipeline_keywords = ["商談", "パイプライン", "見込み", "案件"]
            if any(keyword in question for keyword in pipeline_keywords):
                if self.detailed_sales_data and "customer_pipeline" in self.detailed_sales_data:
                    context_parts.append("【現在の主要商談状況】")
                    pipeline = self.detailed_sales_data["customer_pipeline"]
                    for customer, info in list(pipeline.items())[:3]:  # 上位3件
                        context_parts.append(f"• {customer}: {info.get('stage', '不明')}段階")
                        context_parts.append(f"  確度{info.get('probability', 0)}%, 予想売上{info.get('expected_value', 0)}万円")
                        context_parts.append(f"  担当: {info.get('担当者', '不明')}")
                    context_parts.append("")
            
            # 効率性データの取得
            efficiency_keywords = ["効率", "生産性", "パフォーマンス"]
            if any(keyword in question for keyword in efficiency_keywords):
                if self.enhanced_metrics and "activity_efficiency" in self.enhanced_metrics:
                    efficiency = self.enhanced_metrics["activity_efficiency"]
                    context_parts.append("【営業効率性データ】")
                    if "calls_per_deal" in efficiency:
                        context_parts.append("成約1件あたりの電話件数:")
                        for member, value in efficiency["calls_per_deal"]["individual"].items():
                            context_parts.append(f"  {member}: {value}件")
                    if "avg_deal_size" in efficiency:
                        context_parts.append("平均案件サイズ:")
                        for member, value in efficiency["avg_deal_size"]["individual"].items():
                            context_parts.append(f"  {member}: {value:,}円")
                    context_parts.append("")
            
            # 顧客関係データの取得
            customer_keywords = ["顧客", "お客", "関係", "満足度"]
            if any(keyword in question for keyword in customer_keywords):
                if self.interaction_history and "customer_interactions" in self.interaction_history:
                    context_parts.append("【主要顧客との関係状況】")
                    interactions = self.interaction_history["customer_interactions"]
                    for customer, info in list(interactions.items())[:3]:  # 上位3件
                        context_parts.append(f"• {customer} (担当: {info.get('担当者', '不明')})")
                        context_parts.append(f"  関係強度: {info.get('relationship_strength', '不明')}")
                        context_parts.append(f"  満足度: {info.get('satisfaction_rating', 'N/A')}")
                        if info.get('interaction_timeline'):
                            latest_interaction = list(info['interaction_timeline'].keys())[0]
                            latest_info = info['interaction_timeline'][latest_interaction]
                            context_parts.append(f"  最新接触: {latest_interaction} ({latest_info.get('type', '不明')})")
                    context_parts.append("")
                        
        except Exception as e:
            print(f"詳細営業データコンテキスト取得エラー: {e}")
            context_parts.append("詳細データの取得中にエラーが発生しました。")
        
        return "\n".join(context_parts) if context_parts else "関連する詳細データが見つかりませんでした。"
    
    def _get_web_search_service(self):
        """Web検索サービスを遅延初期化"""
        if self.web_search_service is None:
            try:
                from services.web_search_service import WebSearchService
                self.web_search_service = WebSearchService()
            except ImportError as e:
                print(f"Web検索サービスのインポートに失敗しました: {e}")
                self.web_search_service = None
        return self.web_search_service
    
    def query_with_fallback_search(self, question: str, category: str = "admin") -> str:
        """DB検索 → 見つからない場合はWeb検索の統合メソッド"""
        
        # 🚨 営業関連はWeb検索を無効化（誤検索防止）
        if category == "sales_query":
            db_result = self.query_sales(question)
            if any(indicator in db_result for indicator in ["見つかりませんでした", "含まれていません", "参考文書には"]):
                return """申し訳ございません。お探しの売上データが見つかりませんでした。

営業データベースの確認が必要です。以下をご確認ください：
- 担当者名が正しいか（高見、辻川、小林、佐藤、田中）
- 期間の指定が正しいか

ご不明な点がございましたら、営業管理部までお問い合わせください。"""
            return db_result
        
        # 1. まずDB検索を実行
        db_result = None
        confidence_threshold = 0.3  # 信頼度の閾値
        
        try:
            if category == "admin" or category == "office":
                db_result = self.query_office(question)
            elif category == "procedures":
                db_result = self.query_procedures(question)
            else:
                db_result = self.query_office(question)  # デフォルト
            
            # DB結果の品質をチェック
            quality_indicators = [
                "申し訳ありません",
                "データベースが初期化されていません",
                "関連するデータベースが",
                "見つかりませんでした",
                "回答を生成できませんでした",
                "含まれていません",
                "情報は含まれていません",
                "参考文書には",
                "取扱説明書やメーカーの公式サポートページ",
                "公式情報を参考にしてください"
            ]
            
            is_low_quality = any(indicator in db_result for indicator in quality_indicators)
            is_too_short = len(db_result.strip()) < 50
            
            # DB結果が良質であれば返す
            if not is_low_quality and not is_too_short:
                print(f"✅ DB検索成功 - カテゴリ: {category}")
                return db_result
                
        except Exception as e:
            print(f"DB検索中にエラー: {e}")
        
        # 2. DB検索が失敗した場合はWeb検索を実行
        print(f"📋 DB検索結果が不十分です。Web検索を実行します...")
        
        web_search_service = self._get_web_search_service()
        if web_search_service:
            try:
                web_result = web_search_service.search_and_answer(question)
                if web_result and "検索結果が見つかりませんでした" not in web_result:
                    print(f"🔍 Web検索成功")
                    # Web検索結果を整形
                    formatted_result = self._format_web_search_result(web_result, question)
                    return formatted_result
                else:
                    print(f"❌ Web検索でも結果が見つかりませんでした")
            except Exception as e:
                print(f"Web検索中にエラー: {e}")
        
        # 3. 両方とも失敗した場合は案内メッセージ
        return f"""申し訳ございません。「{question}」について、社内データベースおよびWeb検索でも適切な回答を見つけることができませんでした。

## 💡 **ご利用方法**

**阪南ビジネスマシンの業務支援**: より具体的にお教えいただけますでしょうか？例えば：

📋 **具体的な質問例**
• 「官需課の高見の今期の売り上げは？」
• 「販売台数の詳細は？」
• 「有給申請の方法は？」

## 📊 **ご利用いただける機能**
• 売上分析：「辻川さんの実績は？」
• 手続きガイド：「有給申請の方法は？」
• 社内規定：「経費精算のルールは？」

お気軽にお試しください！"""
    
    def query_detailed_sales(self, question: str, conversation_history: str = "") -> str:
        """詳細営業データ専用クエリ（みなみちゃんキャラクター）"""
        detailed_context = self._get_detailed_sales_context(question)
        
        # 基本売上データも取得
        basic_sales_context = ""
        if self.sales_vectorstore:
            docs = self.sales_vectorstore.similarity_search(question, k=2)
            basic_sales_context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt_template = """
        あなたは阪南ビジネスマシンの営業現場を知り尽くした先輩「みなみちゃん」です。
        
        ## みなみちゃんのキャラクター
        - 親しみやすく温かい標準語での口調
        - 営業の数字の背景や意味まで分かりやすく説明
        - 良い結果は一緒に喜び、課題は一緒に考える姿勢
        - 必ず会話を続ける質問や提案で終わる
        - 実務的なアドバイスを自然に織り込む

        ## これまでの会話
        {history}

        ## 基本売上データ
        {basic_context}
        
        ## 詳細営業活動データ
        {detailed_context}
        
        ## 現在のご質問
        {question}
        
        ## みなみちゃんの応答指針
        1. **具体的な活動数値**: 訪問件数、電話件数、メール件数など具体的データを活用
        2. **パーソナル化**: 個人の特徴や強みを踏まえたアドバイス
        3. **実務的価値**: 明日から使える具体的な改善提案
        4. **親しみやすさ**: 温かい標準語で、親近感のある表現
        5. **会話継続**: 必ず次の質問や相談で会話を続ける
        
        ## 応答例
        「高見さんの今日の訪問件数、6件でしたね！ 電話も12件、メールも8件と、とても精力的に動いていらっしゃいます。
        
        特に堺市消防局、堺市長寿支援課、岸和田市立消費生活センターと、継続顧客をしっかりフォローされてるのが素晴らしいですね。高見さんの強みは、やはりこの継続的な関係維持だと思います。
        
        商談も2件進行中で、売上予測180万円。これ、月末に向けて良い感じのペースですよ！
        
        ただ、もし新規開拓にも少し力を入れるとしたら、どんな分野に興味ありますか？ 高見さんの丁寧なフォロー力なら、新規のお客さんにもきっと信頼してもらえると思うのですが...」
        
        このような調子で、具体的で親しみやすく、かつ実務的価値のある応答をお願いします。
        """
        
        prompt = prompt_template.format(
            history=conversation_history,
            basic_context=basic_sales_context,
            detailed_context=detailed_context,
            question=question
        )
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"詳細営業データ分析中にエラーが発生しました: {e}"
    
    def _format_web_search_result(self, web_result: str, question: str) -> str:
        """Web検索結果を整形して見やすい形式に変換"""
        
        # 複合機関連の情報を整形
        if "複合機" in question or "フラッグシップ" in question:
            return self._format_product_info(web_result, question)
        
        # その他の情報は一般的な整形
        return self._format_general_info(web_result, question)
    
    def _format_product_info(self, web_result: str, question: str) -> str:
        """複合機・製品情報の整形"""
        
        # 重複情報を除去
        cleaned_result = self._remove_duplicates(web_result)
        
        # 製品情報構造化のプロンプト
        format_prompt = f"""
        以下のWeb検索結果を、ユーザーにとって見やすく構造化してください。

        ## 整形指針
        1. 製品名を明確に提示
        2. 主要スペックを箇条書きで簡潔に
        3. 重複情報は除去
        4. 自然な会話形式で回答
        5. 関連情報は簡潔にまとめる
        6. ソース情報も含める（既にある場合はそのまま残す）

        ## ユーザーの質問
        {question}

        ## Web検索結果（整形前）
        {cleaned_result[:1500]}

        ## 整形後の回答
        以下の形式で自然な会話として回答してください：

        [確認メッセージがある場合はそのまま残す]

        [製品名]の主な特徴は以下の通りです：

        ## 📋 主な仕様
        • **項目1**: 内容
        • **項目2**: 内容
        • **項目3**: 内容

        [その他の関連情報があれば簡潔に]

        [ソース情報があれば「## 📚 参考情報」として残す]

        何か他にお聞きになりたいことはありますか？
        """
        
        try:
            response = self.model.invoke(format_prompt)
            return response.content
        except Exception as e:
            print(f"製品情報整形中にエラー: {e}")
            return cleaned_result
    
    def _format_general_info(self, web_result: str, question: str) -> str:
        """一般情報の整形"""
        
        # 重複情報を除去
        cleaned_result = self._remove_duplicates(web_result)
        
        # 一般情報構造化のプロンプト
        format_prompt = f"""
        以下のWeb検索結果を、ユーザーにとって読みやすく整理してください。

        ## 整形指針
        1. 重要な情報を最初に提示
        2. 関連性の低い情報は除去
        3. 自然な会話形式で回答
        4. 箇条書きは最小限に

        ## ユーザーの質問
        {question}

        ## Web検索結果（整形前）
        {cleaned_result[:1500]}

        ## 整形後の回答
        質問に直接答える形で、自然な文章として回答してください。
        """
        
        try:
            response = self.model.invoke(format_prompt)
            return response.content
        except Exception as e:
            print(f"一般情報整形中にエラー: {e}")
            return cleaned_result
    
    def _remove_duplicates(self, text: str) -> str:
        """重複する文や情報を除去"""
        
        # 改行で分割
        lines = text.split('\n')
        unique_lines = []
        seen_content = set()
        
        for line in lines:
            # 空行や短すぎる行はスキップ
            if len(line.strip()) < 10:
                continue
            
            # 同じような内容の重複をチェック
            line_clean = line.strip().lower()
            line_clean = ''.join(c for c in line_clean if c.isalnum() or c.isspace())
            
            # 類似度チェック（簡易版）
            is_duplicate = False
            for seen in seen_content:
                if self._calculate_similarity(line_clean, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_lines.append(line.strip())
                seen_content.add(line_clean)
                
                # 最大行数制限
                if len(unique_lines) >= 15:
                    break
        
        return '\n'.join(unique_lines)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算（簡易版）"""
        
        if not text1 or not text2:
            return 0.0
        
        # 共通する単語の割合を計算
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
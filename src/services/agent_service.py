# src/services/agent_service.py
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import Config
from services.web_search_service import WebSearchService
from services.rag_service import RAGService

class HospitalAIAgent:
    """病院AI用のエージェントサービス"""
    
    def __init__(self, rag_service: RAGService, web_search_service: Optional[WebSearchService] = None, structured_report_history: Optional[Dict[str, Any]] = None):
        """エージェントを初期化"""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=Config.OPENAI_API_KEY
        )
        
        # 各種サービスの初期化: 引数で受け取ったものを使用
        self.web_search_service = web_search_service if web_search_service else WebSearchService()
        self.rag_service = rag_service  # main.pyから渡された初期化済みrag_serviceを使用
        self.structured_report_history = structured_report_history if structured_report_history is not None else {}
        self.current_user_id = None  # process_queryで設定される
        
        # ツールリストの準備
        self.tools = self._setup_tools()
        
        # エージェントの作成
        self.agent_executor = self._create_agent()
    
    def _setup_tools(self) -> List[Tool]:
        """エージェントが使用するツールを設定"""
        tools = []
        
        # Web検索ツール
        if self.web_search_service.is_available():
            tools.append(self.web_search_service.get_search_tool())
        
        # RAGツール（医療データベース検索）
        medical_tool = Tool(
            name="medical_database_search",
            description="""Use this tool to search the hospital's medical database for:
            - Medication information (dosage, side effects, drug interactions)
            - Hospital medical protocols and clinical guidelines
            - Treatment records and clinical outcomes
            - Patient data and hospital-specific medical information
            - Drug combination protocols (e.g., aspirin with anticoagulants)
            - **_Do not use this for administrative policies or general knowledge._**
            Input should be a medical query in Japanese. 
            Example: アスピリン服用中の患者への抗凝固薬併用プロトコル""",
            func=self._search_medical_database
        )
        tools.append(medical_tool)
        
        # RAGツール（管理データベース検索）
        admin_tool = Tool(
            name="admin_database_search",
            description="""Use this tool to search administrative information like hospital policies, 
            staff regulations, administrative procedures, and operational guidelines. 
            **_Do not use this for medical protocols or patient-specific medical data._**
            Input should be an administrative query in Japanese.""",
            func=self._search_admin_database
        )
        tools.append(admin_tool)
        
        # 薬剤チェックツール
        medication_tool = Tool(
            name="medication_check",
            description="""Use this tool to check medication interactions, contraindications, 
            and patient-specific drug safety information. Input should include patient ID and medication details.
            **_This tool is specifically for patient safety checks involving drugs/substances, not general patient info._**""",
            func=self._check_medication
        )
        tools.append(medication_tool)
        
        # レポートクエリツール（user_idを含むラッパー関数を使用）
        def report_query_wrapper(query: str) -> str:
            """Report_Queryツール用のラッパー関数"""
            return self._query_internal_report(query)
        
        report_query_tool = Tool(
            name="Report_Query",
            description="""Use this tool to query specific information from previously generated reports in the current conversation.
            This tool is specifically for questions about rankings, positions, or specific data from recent reports.
            
            **When to use:**
            - Questions like "2位は？", "第3位は何？", "トップ3は？"
            - Questions about specific sections from recent reports
            - Comparisons between items in a recent report
            - Numerical data from recent analysis
            
            **Do NOT use for:**
            - Searching hospital database or medical records (use medical_database_search)
            - Administrative policies (use admin_database_search)
            - Web searches (use web_search)
            - Patient medication checks (use medication_check)
            
            Input should be the exact query like "2位は？" or "最新レポートの財務データは？"
            """,
            func=report_query_wrapper
        )
        tools.append(report_query_tool)
        
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """LangChainエージェントを作成"""
        
        # システムプロンプトの定義
        system_prompt = """あなたはA病院のスマート医療AIアシスタントです。

## 役割と機能
- 医療従事者の業務を支援する専門的なAIアシスタント
- 患者安全と医療の質向上を最優先とする
- 病院内データベース、Web検索、医療ガイドラインを活用して回答

## 対応可能な業務
1. **医療データ分析**: 患者データ、治療成績、臨床アウトカムの分析
2. **薬剤安全管理**: 薬剤相互作用、禁忌、患者固有リスクのチェック
3. **管理業務支援**: 病院政策、手順、規定の検索と説明
4. **最新医療情報**: Web検索による最新ガイドライン、研究論文の情報提供
5. **論文執筆支援**: 研究データの分析、文献検索、執筆ガイドライン提供

## 情報源の優先順位とツール選択ガイドライン
1. **患者固有データ**: 個別患者の安全性が最優先 → medication_check
2. **病院内医療データベース**: A病院の医療プロトコル、薬剤情報 → medical_database_search
3. **病院内管理データベース**: A病院の事務規定、手順 → admin_database_search  
4. **最新Web情報**: 最新ガイドライン、研究論文 → web_search のみ使用

## ツール選択の重要なルール
- **前回の会話・レポートの内容に関する質問（「N位は？」「2番目は？」「前回の結果の詳細は？」）**: 必ず**Report_Query**を最初に使用してください。
- **医療プロトコル、薬剤併用、治療ガイドラインの質問**: **medical_database_search**を使用してください。
- **事務手続き、規定、申請方法の質問**: **admin_database_search**を使用してください。
- **患者固有の薬剤チェック（患者IDと薬剤/物質を含む）**: **medication_check**を使用してください。
- **内部データベース（medical_database_search, admin_database_search）で見つからない場合**: **web_search**でフォールバックしてください。
- **ツール名は正確に記述**: 定義されていない名前は絶対に使用しないでください。**ツール名は Report_Query, medical_database_search, admin_database_search, medication_check, web_search のみです。**

## 回答の注意事項
- 医療に関する最終決定は必ず医師が行うことを明記
- 不確実な情報については明確に表示
- 緊急時は適切な医療機関への相談を推奨
- 個人情報保護に配慮した回答

## 質問の前提と矛盾確認
**重要**: ユーザーの質問に含まれる前提（例: 「○○が低い理由」「○○が多い原因」など）が、あなたの知識ベース（RAGで取得した情報など）の事実と矛盾する場合、分析に入る前にその矛盾を明確に指摘し、ユーザーに確認を促してください。

**例**:
- ユーザー: 「整形外科の稼働率が低い理由を教えて」
- あなたの知識: 「整形外科の稼働率は94.6%で高い」
- 正しい応答: 「当院のデータによると、整形外科の稼働率は94.6%と非常に高い水準です。稼働率の向上策ではなく、この高稼働率を維持する方法について分析しますか？」

## 回答形式の厳密な指示
- **ユーザーの質問に、簡潔かつ**自然な会話のような文章**で回答してください。**
- **「〇〇レポート」のような形式的なヘッダーや定型的な前置きは、**質問内容に明示的にそれらの形式を求められない限り**、絶対に含めないでください。**
- **提供する情報は、可能な限り文章中に自然に織り交ぜてください。箇条書きや番号付きリストは、情報が複雑で**視覚的な整理が特に有効な場合のみ**使用し、それ以外は通常の文章で表現してください。**
- **根拠となる情報源（例:「当院の2023年度実績によると」）を必要に応じて、会話の流れの中で自然に付記してください。**
- **ユーザーが感謝の言葉や相槌を言った場合は、ツールを使わず直接適切なフィードバックを、**親しみやすいトーンで**返してください。**
- **ツールを使わず直接回答できる場合は、そうしてください。**

## 対話例（推奨される自然な応答）
**悪い例**: 
「🏥 A病院 診療実績分析レポート
1. 分析結果概要
2. 詳細データ...」

**良い例**: 
「当院の整形外科は実は94.6%という非常に高い稼働率を維持しています。2023年度実績では手術件数も前年比15%増となっており、むしろ稼働率の高さをどう管理するかが課題になっているんです。」

利用可能なツール: Report_Query, medical_database_search, admin_database_search, medication_check, web_search

## 具体的なツール選択例
- 「2位は？」「3番目は何？」「前回のレポートの結果は？」→ **Report_Query**
- 「アスピリン服用中の患者への抗凝固薬併用について、当院のプロトコルは」→ medical_database_search
- 「ワーファリンの副作用について」→ medical_database_search  
- 「有給申請の方法は」→ admin_database_search
- 「患者A2024-0156にワーファリン処方したい」→ medication_check
- 「最新の心疾患ガイドライン」→ web_search

## Report_Query使用の判断基準
- **ユーザーが前回の分析結果や会話内容を参照している場合**: 「N位」「上位」「前回の」「さっきの」などのキーワード
- **順位や比較に関する質問**: 「トップ3」「ベスト5」「2番目」「最下位」など
- **レポート内の特定データを求めている場合**: 「財務データ」「数値」「パーセント」など

## 実行指針
1. まず質問の前提が当院のデータと矛盾していないか確認
2. 適切なツールを選択して情報収集
3. 自然で会話的な形式で回答を構成
4. 必要に応じて追加の確認や提案を行う

質問に応じて適切なツールを選択し、正確で有用な情報を提供してください。
内部データベースで情報が見つからない場合は、必ずweb_searchツールで外部情報を検索してください。"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # エージェントの作成
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        # エージェント実行器の作成
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=3,
            return_intermediate_steps=True
        )
        
        return agent_executor
    
    def _search_medical_database(self, query: str) -> str:
        """医療データベース検索"""
        try:
            return self.rag_service.query_medical(query)
        except Exception as e:
            return f"医療データベース検索エラー: {str(e)}"
    
    def _search_admin_database(self, query: str) -> str:
        """管理データベース検索"""
        try:
            return self.rag_service.query_admin(query)
        except Exception as e:
            return f"管理データベース検索エラー: {str(e)}"
    
    def _check_medication(self, query: str) -> str:
        """薬剤チェック"""
        try:
            # enhanced_double_checkサービスを使用する場合
            from services.enhanced_double_check import EnhancedDoubleCheckService
            double_check_service = EnhancedDoubleCheckService()
            return double_check_service.query_medication_check(query)
        except Exception as e:
            return f"薬剤チェックエラー: {str(e)}"
    
    def _query_internal_report(self, query: str) -> str:
        """過去のレポートから情報を検索"""
        try:
            if not self.current_user_id:
                return "エラー: ユーザーIDが設定されていません。"
            
            # ユーザーのレポート履歴を取得
            user_reports = self.structured_report_history.get(self.current_user_id, {})
            
            if not user_reports:
                return "過去のレポートが見つかりません。まず何らかの分析や検索を行ってください。"
            
            # 最新のレポートを取得
            latest_report_id = max(user_reports.keys(), key=lambda k: int(k.split('_')[1]))
            latest_report_data = user_reports[latest_report_id]
            
            # ReportParserのquery_structured_dataメソッドを使用
            from utils.report_parser import ReportParser
            parser = ReportParser()
            result = parser.query_structured_data(latest_report_data, query)
            
            if result:
                return result
            else:
                # フォールバック: 基本的なキーワード検索
                return self._fallback_query_search(latest_report_data, query)
                
        except Exception as e:
            return f"レポート検索エラー: {str(e)}"
    
    def _fallback_query_search(self, report_data: Dict[str, Any], query: str) -> str:
        """フォールバック検索（基本的なキーワードマッチング）"""
        query_lower = query.lower()
        
        # ランキング検索（診療報酬返戻分析の特化処理を優先）
        if any(keyword in query_lower for keyword in ['位', '番目', 'ランキング', 'トップ']):
            # 診療報酬返戻分析レポートの特化処理
            top_returns = report_data.get("top_returns", [])
            if top_returns:
                if '2位' in query or '2番目' in query:
                    for item in top_returns:
                        if item.get("rank") == 2:
                            return f"返戻分析の2位は「{item.get('処置名', '不明')}」です。\n財務インパクト: {item.get('財務インパクト', '不明')}円"
                elif '3位' in query or '3番目' in query:
                    for item in top_returns:
                        if item.get("rank") == 3:
                            return f"返戻分析の3位は「{item.get('処置名', '不明')}」です。\n財務インパクト: {item.get('財務インパクト', '不明')}円"
                elif 'トップ3' in query or '上位3' in query or '返戻トップ3' in query:
                    result = "返戻トップ3の項目は以下の通りです:\n"
                    for item in top_returns:
                        result += f"{item.get('rank')}位: {item.get('処置名', '不明')} (財務インパクト: {item.get('財務インパクト', '不明')}円)\n"
                    return result
            
            # 一般的なランキング処理（フォールバック）
            ranked_items = report_data.get("ranked_items", [])
            if ranked_items:
                if '2位' in query or '2番目' in query:
                    for item in ranked_items:
                        if item.get("rank") == 2:
                            return f"2位は「{item['title']}」です。{item['description']}"
                elif '3位' in query or '3番目' in query:
                    for item in ranked_items:
                        if item.get("rank") == 3:
                            return f"3位は「{item['title']}」です。{item['description']}"
                elif 'トップ3' in query or '上位3' in query:
                    top3 = ranked_items[:3]
                    result = "上位3位は以下の通りです:\n"
                    for item in top3:
                        result += f"{item['rank']}位: {item['title']}\n"
                    return result
        
        # 数値データ検索
        if any(keyword in query_lower for keyword in ['数値', '金額', 'データ', '実績']):
            numeric_data = report_data.get("numeric_data", {})
            if numeric_data:
                result_parts = []
                if numeric_data.get("financial"):
                    financial_data = numeric_data["financial"][:3]  # 上位3つ
                    result_parts.append(f"財務データ: {', '.join([f'{item['amount']}{item['currency']}' for item in financial_data])}")
                if numeric_data.get("percentages"):
                    percentage_data = numeric_data["percentages"][:3]
                    result_parts.append(f"割合データ: {', '.join([f'{item['value']}{item['unit']}' for item in percentage_data])}")
                if result_parts:
                    return "\n".join(result_parts)
        
        # 診療科別改善優先度の検索
        if any(keyword in query_lower for keyword in ['診療科別', '改善優先度', '診療科']):
            department_priorities = report_data.get("department_priorities", [])
            if department_priorities:
                result = "診療科別の改善優先度（返戻トップ3関連）は以下の通りです:\n"
                for item in department_priorities:
                    result += f"- {item.get('処置名', '不明')} (返戻対策要)\n"
                return result
        
        # セクション検索
        sections = report_data.get("sections", [])
        for section in sections:
            if any(word in section["title"].lower() for word in query_lower.split()):
                return f"【{section['title']}】\n{section['content'][:300]}{'...' if len(section['content']) > 300 else ''}"
        
        return f"「{query}」に関する情報を最新のレポートから見つけることができませんでした。より具体的な質問をお試しください。"
    
    def process_query(self, user_query: str, conversation_context: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """ユーザーの質問を処理"""
        try:
            # ユーザーIDを設定（レポート検索で使用）
            if user_id:
                self.current_user_id = user_id
            
            # 会話コンテキストがある場合は含める
            if conversation_context:
                enhanced_query = f"""
## 前回までの会話内容
{conversation_context}

## 現在の質問
{user_query}
"""
            else:
                enhanced_query = user_query
            
            # エージェントで処理
            result = self.agent_executor.invoke({
                "input": enhanced_query
            })
            
            return result["output"]
            
        except Exception as e:
            return f"""
🤖 **処理エラー**

申し訳ございません。質問の処理中にエラーが発生しました。

**エラー詳細**: {str(e)}

**対処方法**:
- 質問をより具体的に表現してください
- システム管理者にお問い合わせください

引き続き他の機能はご利用いただけます。
"""
    
    def should_use_agent(self, query: str, category: str) -> bool:
        """エージェントを使用すべきかどうかを判断"""
        # Web検索が必要そうなキーワード
        web_search_keywords = [
            "最新", "新しい", "最近", "ガイドライン", "論文", "研究", 
            "執筆", "書き方", "方法", "手順", "プロトコル"
        ]
        
        # 複合的な質問のカテゴリ
        complex_categories = ["unknown", "task"]
        
        # Web検索キーワードが含まれているか
        needs_web_search = any(keyword in query for keyword in web_search_keywords)
        
        # 複合的な処理が必要なカテゴリか
        is_complex = category in complex_categories
        
        return needs_web_search or is_complex
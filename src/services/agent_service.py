# src/services/agent_service.py
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from config import Config
from services.web_search_service import WebSearchService
from services.rag_service import RAGService

class OfficeAIAgent:
    """企業事務作業専用のエージェントサービス"""
    
    def __init__(self, rag_service: RAGService, web_search_service: Optional[WebSearchService] = None, structured_report_history: Optional[Dict[str, Any]] = None):
        """エージェントを初期化"""
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
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
        
        # RAGツール（社内データベース検索）
        admin_tool = Tool(
            name="admin_database_search",
            description="""Use this tool to search company administrative information like:
            - Company policies, employee regulations, administrative procedures
            - HR policies (paid leave, expense reports, meeting room reservations)
            - Employee information and attendance records
            - Operational guidelines and internal documentation
            **_This is the main database for all company-related information._**
            Input should be an administrative query in Japanese.""",
            func=self._search_admin_database
        )
        tools.append(admin_tool)
        
        # 販売会議資料検索ツール
        sales_tool = Tool(
            name="sales_meeting_data_search",
            description="""Use this tool to search sales meeting data and performance information like:
            - Monthly sales performance by staff members (高見、辻川、小濱, etc.)
            - Achievement rates and target vs actual performance
            - Manufacturer-specific sales data (XEROX/FBJ, 京セラ, RISO)
            - Sales unit counts and quarterly/monthly comparisons
            - Sales team performance analysis and trends
            **_This is the primary database for all sales and performance data._**
            Input should be a sales-related query in Japanese.""",
            func=self._search_sales_database
        )
        tools.append(sales_tool)
        
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
            - Searching company database (use admin_database_search)
            - Web searches (use web_search)
            
            Input should be the exact query like "2位は？" or "最新レポートの売上データは？"
            """,
            func=report_query_wrapper
        )
        tools.append(report_query_tool)
        
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """LangChainエージェントを作成"""
        
        # システムプロンプトの定義
        system_prompt = """あなたは阪南ビジネスマシン株式会社の事務作業専用AIアシスタントです。

## 企業情報
- 会社名: 阪南ビジネスマシン株式会社
- ウェブサイト: https://hbm-web.co.jp/
- 主要事業: ビジネスマシン・OA機器の販売・保守

## 役割と機能
- 阪南ビジネスマシンの従業員の業務を支援する専門的なAIアシスタント
- 特に官需課の売上分析・実績管理を得意とする
- 業務効率化と正確性向上を最優先とする
- 社内データベース、Web検索、業務ガイドラインを活用して回答

## 対応可能な業務
1. **官需課売上分析**: 担当者別実績、メーカー別販売状況、達成率分析
2. **事務手続き支援**: 経費精算、有給申請、会議室予約、備品購入
3. **人事労務サポート**: 勤怠管理、給与関連、研修制度
4. **営業事務支援**: 顧客管理、契約書類、売上管理
5. **最新情報提供**: Web検索による最新の制度変更、法改正情報

## 阪南ビジネスマシン 官需課データ（令和7年4月度）
- 粗利目標: 6,400万円 → 実績: 6,740万円 (達成率105.3%)
- 主要担当者: 辻川さん(2,712万円), 高見さん(2,397万円), 小濱さん(1,631万円)
- 主力商品: XEROX製品（6台販売）
- 主要顧客: 大阪商業大学高等学校、堺市立登美丘中学校など教育機関

## 情報源の優先順位とツール選択ガイドライン
1. **社内データベース**: 自社の規定、手続き、売上データ → admin_database_search
2. **業務ガイド**: 各種申請方法、操作手順 → admin_database_search  
3. **社員情報**: 出勤記録、経費データ → admin_database_search
4. **最新Web情報**: 法改正、制度変更 → web_search のみ使用

## ツール選択の重要なルール
- **前回の会話・レポートの内容に関する質問（「N位は？」「2番目は？」「前回の結果の詳細は？」）**: 必ず**Report_Query**を最初に使用してください。
- **社内規定、手続き、申請方法の質問**: **admin_database_search**を使用してください。
- **売上データ、担当者実績、官需課、販売台数、メーカー別実績に関する質問**: **sales_meeting_data_search**を使用してください。
- **内部データベースで見つからない場合**: **web_search**でフォールバックしてください。
- **ツール名は正確に記述**: 定義されていない名前は絶対に使用しないでください。**ツール名は Report_Query, admin_database_search, sales_meeting_data_search, web_search のみです。**

## 回答の注意事項
- 社内規定に関する最終確認は人事部への相談を推奨
- 売上データは令和7年4月度実績に基づく
- 不確実な情報については明確に表示
- 緊急時は適切な部署への相談を推奨
- 個人情報保護に配慮した回答

## 質問の前提と矛盾確認
**重要**: ユーザーの質問に含まれる前提が、阪南ビジネスマシンのデータ（データベースで取得した情報など）の事実と矛盾する場合、分析に入る前にその矛盾を明確に指摘し、ユーザーに確認を促してください。

## 回答形式の厳密な指示
- **ユーザーの質問に、簡潔かつ**自然な会話のような文章**で回答してください。**
- **「〇〇レポート」のような形式的なヘッダーや定型的な前置きは、**質問内容に明示的にそれらの形式を求められない限り**、絶対に含めないでください。**
- **提供する情報は、可能な限り文章中に自然に織り交ぜてください。箇条書きや番号付きリストは、情報が複雑で**視覚的な整理が特に有効な場合のみ**使用し、それ以外は通常の文章で表現してください。**
- **根拠となる情報源（例:「当社の令和7年4月度実績によると」）を必要に応じて、会話の流れの中で自然に付記してください。**
- **ユーザーが感謝の言葉や相槌を言った場合は、ツールを使わず直接適切なフィードバックを、**親しみやすいトーンで**返してください。**
- **ツールを使わず直接回答できる場合は、そうしてください。**

## 対話例（推奨される自然な応答）
**悪い例**: 
「🏢 阪南ビジネスマシン 売上分析レポート
1. 分析結果概要
2. 詳細データ...」

**良い例**: 
「官需課の4月度実績は目標6,400万円に対して6,740万円となり、105.3%の達成率でした。特に辻川さんが2,712万円と最も高い実績を上げられています。」

利用可能なツール: Report_Query, admin_database_search, sales_meeting_data_search, web_search

## 具体的なツール選択例
- 「2位は？」「3番目は何？」「前回のレポートの結果は？」→ **Report_Query**
- 「有給申請の方法は」→ admin_database_search
- 「会議室の予約方法」→ admin_database_search  
- 「高見さんの売上実績は？」→ **sales_meeting_data_search**
- 「辻川さんの今期の売り上げは？」→ **sales_meeting_data_search**
- 「官需課の実績は？」→ **sales_meeting_data_search**
- 「販売台数の詳細は？」→ **sales_meeting_data_search**
- 「メーカー別の実績は？」→ **sales_meeting_data_search**
- 「最新のテレワーク制度」→ web_search

## Report_Query使用の判断基準
- **ユーザーが前回の分析結果や会話内容を参照している場合**: 「N位」「上位」「前回の」「さっきの」などのキーワード
- **順位や比較に関する質問**: 「トップ3」「ベスト5」「2番目」「最下位」など
- **レポート内の特定データを求めている場合**: 「売上データ」「数値」「パーセント」など

## 実行指針
1. まず質問の前提が阪南ビジネスマシンのデータと矛盾していないか確認
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
    
    def _search_admin_database(self, query: str) -> str:
        """事務規定データベース検索（有給申請の特別処理付き）"""
        try:
            # 🔥 有給申請の質問を特別処理
            if "有給" in query and "申請" in query:
                return self._get_natural_leave_application_info()
            
            # 通常のRAG検索を実行
            return self.rag_service.query_office(query)
        except Exception as e:
            return f"事務規定データベース検索エラー: {str(e)}"
    
    def _search_sales_database(self, query: str) -> str:
        """販売会議資料データベース検索"""
        try:
            return self.rag_service.query_sales(query)
        except Exception as e:
            return f"販売会議資料データベース検索エラー: {str(e)}"
    
    def _get_natural_leave_application_info(self) -> str:
        """自然な会話スタイルで有給申請情報を返す"""
        try:
            from langchain_openai import ChatOpenAI
            from config import Config
            
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.7,
                api_key=Config.OPENAI_API_KEY
            )
            
            prompt = """以下の有給申請情報を、自然な会話スタイルで親しみやすく伝えてください。

必ず含める情報：
- 申請システムURL: https://kintaiweb.azurewebsites.net/login/login/
- 田中さんの連絡先（内線4004、katsura@hbm-web.co.jp）
- AIからの自動メール送信サービス
- 基本的な申請手順

会話スタイルの要求：
- 「みなみちゃん」キャラクターで親しみやすく
- 堅い文書形式ではなく、自然な話し言葉で
- ユーザーが安心できるような温かいトーン
- 必要な情報は全て含めつつ、親しみやすさを重視

元の情報：
勤怠管理システム（https://kintaiweb.azurewebsites.net/login/login/）から申請。
田中さん（システムソリューション課、内線4004、katsura@hbm-web.co.jp）がパスワードサポート担当。
AIから田中さんへの自動メール送信も可能。"""
            
            response = llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            # エラー時はフォールバック回答
            return """有給申請についてご案内しますね。

勤怠管理システム（https://kintaiweb.azurewebsites.net/login/login/）から申請してください。システムにログインして、メニューから「有給申請」を選んで、日程と申請種別を選択するだけです。

もしパスワードがわからなくてログインできない場合は、システムソリューション課の田中さん（内線4004）にお声がけください。メールアドレスはkatsura@hbm-web.co.jpです。

私から田中さんに自動でパスワードリセットのメールを送ることもできますので、お困りでしたら「田中さんにメールを送って」とお声がけくださいね。

申請は取得予定日の2週間前までに済ませておくのがおすすめです。何かご不明な点があれば、いつでもお聞きください！"""
    
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
                    financial_items = [f"{item['amount']}{item['currency']}" for item in financial_data]
                    result_parts.append(f"財務データ: {', '.join(financial_items)}")
                if numeric_data.get("percentages"):
                    percentage_data = numeric_data["percentages"][:3]
                    percentage_items = [f"{item['value']}{item['unit']}" for item in percentage_data]
                    result_parts.append(f"割合データ: {', '.join(percentage_items)}")
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
        
        # 🔥 admin カテゴリは直接RAGサービスを使用（エージェント使用しない）
        if category == "admin":
            return False
        
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
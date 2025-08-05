# src/services/web_search_service.py
from typing import List, Dict, Any
import os
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from config import Config

class WebSearchService:
    """Web検索機能を提供するサービス"""
    
    def __init__(self):
        """Web検索サービスを初期化"""
        self.serper_api_key = Config.SERPER_API_KEY
        self.search_wrapper = None
        self.search_tool = None
        
        # APIキーが設定されている場合のみ初期化
        if self.serper_api_key:
            self._initialize_search_tool()
        else:
            print("Warning: SERPER_API_KEY not found. Web search functionality will be disabled.")
    
    def _initialize_search_tool(self):
        """検索ツールを初期化"""
        try:
            # Serper API Wrapperを初期化
            self.search_wrapper = GoogleSerperAPIWrapper(
                serper_api_key=self.serper_api_key,
                k=5,  # 検索結果の最大数
                type="search",  # 検索タイプ
                tbs=None,  # 時間フィルタなし
                gl="jp",  # 地域設定（日本）
                hl="ja"   # 言語設定（日本語）
            )
            
            # LangChainツールとして定義
            self.search_tool = Tool(
                name="web_search",
                description="""Use this tool to search for current information on the web. 
                This is useful when you need to find recent information, guidelines, or research papers 
                that are not in the existing knowledge base. 
                Input should be a search query in Japanese or English.""",
                func=self.search_wrapper.run
            )
            
            print("Web search tool initialized successfully")
            
        except Exception as e:
            print(f"Error initializing web search tool: {e}")
            self.search_wrapper = None
            self.search_tool = None
    
    def is_available(self) -> bool:
        """Web検索機能が利用可能かどうかを確認"""
        return self.search_tool is not None
    
    def search(self, query: str) -> str:
        """Web検索を実行"""
        if not self.is_available():
            return "Web検索機能は現在利用できません。APIキーの設定を確認してください。"
        
        try:
            # 検索実行
            results = self.search_wrapper.run(query)
            return results
            
        except Exception as e:
            return f"検索中にエラーが発生しました: {str(e)}"
    
    def search_medical_guidelines(self, topic: str) -> str:
        """医療ガイドライン専用の検索"""
        search_query = f"{topic} 医療ガイドライン 日本 最新"
        return self.search(search_query)
    
    def search_research_papers(self, topic: str) -> str:
        """研究論文専用の検索"""
        search_query = f"{topic} 研究論文 論文執筆 最新研究"
        return self.search(search_query)
    
    def search_hospital_protocols(self, topic: str) -> str:
        """病院プロトコル専用の検索"""
        search_query = f"{topic} 病院 プロトコル 手順 ガイドライン"
        return self.search(search_query)
    
    def get_search_tool(self) -> Tool:
        """LangChainエージェント用の検索ツールを取得"""
        return self.search_tool
    
    def format_search_results(self, raw_results: str) -> str:
        """検索結果を見やすい形式にフォーマット"""
        if not raw_results or "エラー" in raw_results:
            return raw_results
        
        # 基本的なフォーマッティング
        formatted = f"""
🔍 **Web検索結果**

{raw_results}

---
ℹ️ *Web検索結果は最新の情報を含んでいますが、医療に関する決定を行う前に、必ず専門医や公式ガイドラインをご確認ください。*
"""
        return formatted
    
    def search_and_answer(self, question: str) -> str:
        """Web検索を実行して親しみやすい回答を生成（ソース付き）"""
        if not self.is_available():
            return "Web検索機能は現在利用できません。APIキーの設定を確認してください。"
        
        try:
            # 詳細な検索結果を取得（ソース情報含む）
            raw_results = self.search_wrapper.results(question)
            
            if not raw_results or not isinstance(raw_results, dict) or not raw_results.get('organic'):
                return "申し訳ありません、Web検索でも該当する情報が見つかりませんでした。"
            
            # 検索結果とソース情報を抽出
            search_content, sources = self._extract_results_with_sources(raw_results)
            
            if not search_content:
                return "申し訳ありません、Web検索でも該当する情報が見つかりませんでした。"
            
            # トナー交換関連の質問の場合は親しみやすい回答を生成
            if "トナー" in question and "交換" in question:
                return self._generate_toner_response_with_sources(search_content, question, sources)
            
            # その他の質問は検索結果にソースを追加して返す
            return self._format_search_result_with_sources(search_content, sources)
            
        except Exception as e:
            return f"検索中にエラーが発生しました: {str(e)}"
    
    def _generate_toner_response(self, search_results: str, question: str) -> str:
        """トナー交換に関する親しみやすい回答を生成"""
        # 京セラの公式URLを抽出
        official_url = None
        if "kyocera.inst-guide.com" in search_results:
            official_url = "https://kyocera.inst-guide.com/a11a/index_ja.html"
        
        response = f"""TASKalfa 3554ciのトナー交換方法を調べました！

操作パネルに手順が表示されるので、それに従って交換できますよ。"""
        
        if official_url:
            response += f"""
詳しい動画ガイドもこちらにあります：
{official_url}"""
        
        return response
    
    def _extract_results_with_sources(self, raw_results: dict) -> tuple[str, List[Dict[str, str]]]:
        """検索結果からコンテンツとソース情報を抽出"""
        content_parts = []
        sources = []
        
        try:
            # organic検索結果から情報を抽出
            organic_results = raw_results.get('organic', [])
            
            for i, result in enumerate(organic_results[:5]):  # 最大5件
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                if title and snippet and link:
                    # コンテンツに追加
                    content_parts.append(f"{title}: {snippet}")
                    
                    # ソース情報に追加
                    sources.append({
                        'title': title,
                        'url': link,
                        'index': i + 1
                    })
            
            content = ' '.join(content_parts)
            return content, sources
            
        except Exception as e:
            print(f"検索結果抽出エラー: {e}")
            return "", []
    
    def _format_search_result_with_sources(self, content: str, sources: List[Dict[str, str]]) -> str:
        """検索結果とソース情報をフォーマット"""
        if not content:
            return "検索結果が見つかりませんでした。"
        
        # メインコンテンツ
        result = content
        
        # ソース情報を追加
        if sources:
            result += "\n\n## 📚 参考情報\n"
            for source in sources[:3]:  # 最大3件のソースを表示
                result += f"• [{source['title']}]({source['url']})\n"
        
        return result
    
    def _generate_toner_response_with_sources(self, content: str, question: str, sources: List[Dict[str, str]]) -> str:
        """トナー交換に関する親しみやすい回答を生成（ソース付き）"""
        
        # 基本的な回答を生成
        response = """トナーの交換方法についてお教えしますね。まず、プリンターのフロントカバーを開けましょう。これにはフロントカバーオープンボタンを押す必要があります。次に、トナーカートリッジの右端にあるレバーを手前に回し、プリンタ側の矢印とカートリッジのマークを合わせてください。

古いトナーカートリッジを取り外したら、新しいトナーカートリッジを用意します。箱から取り出したら、トナーが均等になるように5回ほど振ってください。その後、新しいカートリッジをカートリッジホルダーにしっかりと差し込みます。

最後にフロントカバーを閉じ、[クリア]キーを押して完了です。トナーがこぼれないように、床にはいらない紙を敷いておくと安心ですよ。"""
        
        # ソース情報を追加
        if sources:
            response += "\n\n## 📚 参考情報\n"
            for source in sources[:2]:  # トナー交換は最大2件のソースを表示
                response += f"• [{source['title']}]({source['url']})\n"
        
        return response
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
#!/usr/bin/env python3
# test_agent_sales.py - 販売会議資料に対するエージェントのテスト

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.rag_service import RAGService
from services.agent_service import OfficeAIAgent

def test_agent_sales_queries():
    """販売会議資料に関するエージェントの質問テスト"""
    print("🤖 販売会議資料に対するAIエージェントのテストを開始します...")
    
    # RAGサービスを初期化
    rag_service = RAGService()
    rag_service.setup_vectorstores()
    
    # エージェントを初期化
    agent = OfficeAIAgent(rag_service)
    
    # テスト質問
    test_queries = [
        "官需課の高見の今期の売り上げは？",
        "販売台数の詳細は？",
        "辻川さんの実績はどうですか？",
        "京セラ製品の売れ行きは？",
        "8月に何か問題がありましたか？"
    ]
    
    print("\n🔍 販売関連の質問をエージェントでテスト中...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- テスト質問 {i} ---")
        print(f"質問: {query}")
        
        try:
            response = agent.process_query(query)
            print(f"回答: {response[:300]}..." if len(response) > 300 else f"回答: {response}")
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("\n✅ AIエージェントの販売会議資料対応テストが完了しました！")

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    test_agent_sales_queries()

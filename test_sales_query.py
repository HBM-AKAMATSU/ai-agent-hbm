#!/usr/bin/env python3
# test_sales_query.py - 販売データクエリの動作テスト

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_router_classification():
    """ルーターの分類テスト"""
    print("🔍 ルーターの分類テストを開始します...")
    
    try:
        from services.router import QuestionRouter
        router = QuestionRouter()
        
        # テスト質問
        test_queries = [
            "官需課の高見の今期の売り上げは？",
            "辻川さんの実績はどうですか？",
            "RISO製品の販売状況は？",
            "営業担当者別の達成率を教えて",
            "今月の売上実績は？"
        ]
        
        print("\n--- ルーター分類結果 ---")
        for query in test_queries:
            try:
                category = router.classify_question(query)
                print(f"質問: {query}")
                print(f"分類: {category}")
                print("---")
            except Exception as e:
                print(f"❌ 分類エラー: {e}")
        
        print("✅ ルーター分類テスト完了")
        
    except Exception as e:
        print(f"❌ ルーターテストエラー: {e}")

def test_rag_service():
    """RAGサービスのテスト"""
    print("\n🔍 RAGサービスのテストを開始します...")
    
    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        rag_service.setup_vectorstores()
        
        # テスト質問
        test_query = "官需課の高見の今期の売り上げは？"
        
        print(f"\n--- RAGサービステスト ---")
        print(f"質問: {test_query}")
        
        if rag_service.sales_vectorstore:
            response = rag_service.query_sales(test_query)
            print(f"回答: {response[:500]}...")
            print("✅ RAGサービステスト完了")
        else:
            print("❌ 販売データベースが読み込まれていません")
        
    except Exception as e:
        print(f"❌ RAGサービステストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 販売データクエリ動作テストを開始します...\n")
    
    test_router_classification()
    test_rag_service()
    
    print("\n🎉 全テスト完了！")

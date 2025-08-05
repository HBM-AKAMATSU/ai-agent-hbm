#!/usr/bin/env python3
# test_sales_db.py - 販売会議資料データベースのテストスクリプト

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.rag_service import RAGService

def test_sales_db():
    """販売会議資料データベースのテスト"""
    print("🧪 販売会議資料データベースのテストを開始します...")
    
    # RAGサービスを初期化
    rag_service = RAGService()
    
    # ベクトルデータベースを読み込み
    print("\n📊 ベクトルデータベースを読み込み中...")
    rag_service.setup_vectorstores()
    
    # テスト質問を実行
    test_questions = [
        "高見さんの7月の実績はどうでしたか？",
        "8月度で何か問題がありましたか？",
        "京セラ製品の販売実績はどうですか？",
        "7月度の全体的な達成率を教えてください",
        "メーカー別の実績推移を教えて"
    ]
    
    print("\n🔍 販売会議資料に関する質問をテスト中...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- テスト質問 {i} ---")
        print(f"質問: {question}")
        
        try:
            response = rag_service.query_sales(question)
            print(f"回答: {response[:200]}..." if len(response) > 200 else f"回答: {response}")
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("\n✅ 販売会議資料データベースのテストが完了しました！")
    
    # 会話履歴付きテスト
    print("\n🗣️ 会話履歴を考慮したテストを実行中...")
    conversation_history = "先ほど高見さんの実績について質問しました。"
    
    try:
        response = rag_service.query_sales_with_history(
            "辻川さんの実績と比較してどうですか？", 
            conversation_history
        )
        print(f"会話履歴付き回答: {response[:300]}..." if len(response) > 300 else f"会話履歴付き回答: {response}")
    except Exception as e:
        print(f"❌ 会話履歴付きテストでエラー: {e}")

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    test_sales_db()

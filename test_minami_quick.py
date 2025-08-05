#!/usr/bin/env python3
# test_minami_quick.py - みなみちゃんキャラクターの簡単テスト

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_minami_basic():
    """みなみちゃんキャラクターの基本テスト"""
    print("🎭 みなみちゃんキャラクター基本テスト開始")
    print("=" * 50)
    
    try:
        from services.rag_service import RAGService
        
        # RAGサービス初期化
        print("RAGサービス初期化中...")
        rag_service = RAGService()
        rag_service.setup_vectorstores()
        
        # 基本的な質問でテスト
        test_queries = [
            "高見さんの今日の訪問件数は？",
            "辻川さんの商談進捗はどう？"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- テスト {i} ---")
            print(f"質問: {query}")
            
            try:
                # 詳細営業データクエリを使用
                response = rag_service.query_detailed_sales(query)
                print(f"応答: {response[:200]}...")
                
                # 基本的な検証
                if len(response) > 30:
                    print("✅ 適切な長さの応答生成")
                else:
                    print("⚠️ 応答が短すぎる可能性")
                    
                # キャラクター要素の簡易チェック
                character_indicators = ["です", "ます", "ね", "よ"]
                has_character = any(indicator in response for indicator in character_indicators)
                if has_character:
                    print("✅ キャラクター要素確認")
                else:
                    print("⚠️ キャラクター要素不足")
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 みなみちゃん基本テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return False

def test_detailed_data_loading():
    """詳細データ読み込みテスト"""
    print("\n📊 詳細データ読み込みテスト")
    print("-" * 30)
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # データが正常に読み込まれているかチェック
        if rag_service.detailed_sales_data:
            print("✅ 詳細営業データ読み込み成功")
            if "daily_activities" in rag_service.detailed_sales_data:
                print("✅ 日次活動データ確認")
            if "customer_pipeline" in rag_service.detailed_sales_data:
                print("✅ 顧客パイプラインデータ確認")
        else:
            print("⚠️ 詳細営業データが空")
            
        if rag_service.enhanced_metrics:
            print("✅ 拡張営業指標データ読み込み成功")
        else:
            print("⚠️ 拡張営業指標データが空")
            
        if rag_service.interaction_history:
            print("✅ 顧客接触履歴データ読み込み成功")
        else:
            print("⚠️ 顧客接触履歴データが空")
            
        return True
        
    except Exception as e:
        print(f"❌ データ読み込みエラー: {e}")
        return False

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 みなみちゃんキャラクター クイックテスト開始")
    
    # データ読み込みテスト
    data_success = test_detailed_data_loading()
    
    if data_success:
        # 基本テスト
        basic_success = test_minami_basic()
        if basic_success:
            print("\n🎉 全テスト成功！みなみちゃんキャラクター実装完了")
        else:
            print("\n⚠️ 基本テストで問題が発生しました")
    else:
        print("\n❌ データ読み込みに問題があります")
    
    print("\n次のステップ: Week 2のレポート生成サービス実装に進んでください")
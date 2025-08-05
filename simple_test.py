#!/usr/bin/env python3
# simple_test.py - シンプルなテスト

import sys
import os

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("🔍 シンプルテスト開始...")

# 1. ルーターテスト
try:
    from services.router import QuestionRouter
    router = QuestionRouter()
    
    query = "官需課の高見の今期の売り上げは？"
    category = router.classify_question(query)
    print(f"質問: {query}")
    print(f"分類結果: {category}")
    
    if category == "sales_query":
        print("✅ ルーター分類成功！")
    else:
        print(f"❌ ルーター分類失敗！期待：sales_query, 実際：{category}")
        
except Exception as e:
    print(f"❌ ルーターエラー: {e}")

print("\n🎉 テスト完了！")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文脈推測機能のテスト
「富士フィルムのフラッグシップモデルは？」→「複合機で」の対話をシミュレート
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.conversation_manager import ConversationManager
from services.router import QuestionRouter

def test_context_conversation():
    print("🧪 文脈推測機能テスト開始")
    print("=" * 50)
    
    # テスト用インスタンス作成
    conversation_manager = ConversationManager()
    router = QuestionRouter()
    test_user_id = "test_user_123"
    
    # 1回目の質問: 「富士フィルムのフラッグシップモデルは？」
    first_query = "富士フィルムのフラッグシップモデルは？"
    first_category = router.classify_question(first_query)
    first_response = "富士フィルムのフラッグシップモデルには、「FUJIFILM X-H2」があります。このモデルは、「X-Trans CMOS 5 HR」センサーを搭載しており、高精細な8K/30Pの映像を撮影できるミラーレスデジタルカメラです。"
    
    print(f"👤 1回目: {first_query}")
    print(f"🏷️  カテゴリ: {first_category}")
    print(f"🤖 回答: {first_response[:100]}...")
    
    # 会話履歴に追加
    conversation_manager.add_message(test_user_id, first_query, first_response, first_category)
    print("✅ 1回目の会話を履歴に保存")
    print()
    
    # 2回目の質問: 「複合機で」
    second_query = "複合機で"
    print(f"👤 2回目: {second_query}")
    
    # 文脈チェック
    has_context = conversation_manager.has_recent_conversation(test_user_id)
    is_incomplete = conversation_manager.is_incomplete_query(second_query)
    
    print(f"🔍 最近の会話あり: {has_context}")
    print(f"🔍 不完全な質問: {is_incomplete}")
    
    # 文脈推測
    if has_context and is_incomplete:
        enhanced_query, was_enhanced = conversation_manager.enhance_query_with_context(test_user_id, second_query)
        
        print(f"🧠 文脈推測実行:")
        print(f"   元の質問: '{second_query}'")
        print(f"   補完結果: '{enhanced_query}'")
        print(f"   補完実行: {was_enhanced}")
        
        if was_enhanced:
            contextual_confirmation = conversation_manager.generate_contextual_confirmation(test_user_id, second_query, enhanced_query)
            print(f"💬 確認メッセージ: '{contextual_confirmation}'")
        
        # カテゴリ分類（補完された質問で）
        second_category = router.classify_question(enhanced_query)
        print(f"🏷️  補完後カテゴリ: {second_category}")
        
    else:
        print("❌ 文脈推測の条件を満たさない")
        enhanced_query = second_query
        was_enhanced = False
        second_category = router.classify_question(second_query)
    
    print()
    print("📋 テスト結果サマリー:")
    print(f"   1回目質問: {first_query}")
    print(f"   2回目質問: {second_query}")
    print(f"   補完後質問: {enhanced_query}")
    print(f"   補完実行: {was_enhanced}")
    
    return {
        "first_query": first_query,
        "second_query": second_query, 
        "enhanced_query": enhanced_query,
        "was_enhanced": was_enhanced,
        "first_category": first_category,
        "second_category": second_category
    }

def test_conversation_context():
    print("\n" + "=" * 50)
    print("🧪 会話コンテキスト取得テスト")
    print("=" * 50)
    
    conversation_manager = ConversationManager()
    test_user_id = "test_user_456"
    
    # 複数の会話を追加
    conversations = [
        ("富士フィルムのフラッグシップモデルは？", "カメラのX-H2です。", "general_chat"),
        ("複合機で", "富士フィルムの複合機でしたら、ApeosPortシリーズですね！", "task"),
        ("価格は？", "ApeosPortシリーズの価格情報をお調べします。", "task")
    ]
    
    for user_msg, ai_response, category in conversations:
        conversation_manager.add_message(test_user_id, user_msg, ai_response, category)
        print(f"✅ 追加: {user_msg} → {ai_response[:30]}...")
    
    # コンテキスト取得
    context = conversation_manager.get_conversation_context(test_user_id)
    print(f"\n📝 取得されたコンテキスト:")
    print(context[:300] + "..." if len(context) > 300 else context)

if __name__ == "__main__":
    try:
        result = test_context_conversation()
        test_conversation_context()
        
        print("\n" + "🎉" * 20)
        print("テスト完了！")
        
        if result["was_enhanced"]:
            print("✅ 文脈推測機能は正常に動作しています")
        else:
            print("❌ 文脈推測機能に問題があります")
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

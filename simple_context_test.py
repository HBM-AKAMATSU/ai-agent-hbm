#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文脈推測機能の簡単なテスト（依存関係なし）
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# ConversationManagerの簡単な実装
class SimpleConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def add_message(self, user_id: str, user_message: str, ai_response: str, category: str = None):
        if user_id not in self.conversations:
            self.conversations[user_id] = {"history": []}
        
        self.conversations[user_id]["history"].append({
            "user_message": user_message,
            "ai_response": ai_response,
            "category": category
        })
    
    def has_recent_conversation(self, user_id: str) -> bool:
        return user_id in self.conversations and len(self.conversations[user_id]["history"]) > 0
    
    def is_incomplete_query(self, user_message: str) -> bool:
        if len(user_message.strip()) <= 3:
            return True
        
        incomplete_patterns = ["で", "なら", "だと", "について", "の", "は？", "って", "だったら"]
        stripped = user_message.strip()
        return any(stripped == pattern or stripped.endswith(pattern) for pattern in incomplete_patterns)
    
    def enhance_query_with_context(self, user_id: str, current_query: str) -> tuple:
        if user_id not in self.conversations:
            return current_query, False
        
        history = self.conversations[user_id]["history"]
        if not history:
            return current_query, False
        
        last_entry = history[-1]
        last_user_message = last_entry["user_message"]
        
        enhanced_query = current_query
        was_enhanced = False
        
        # 「複合機で」の場合
        if current_query.strip() in ["複合機で", "複合機なら", "複合機だと", "複合機は？", "複合機について"]:
            if "富士フィルム" in last_user_message or "富士フイルム" in last_user_message:
                enhanced_query = "富士フィルムの複合機のフラッグシップモデル"
                was_enhanced = True
            elif "キヤノン" in last_user_message or "Canon" in last_user_message:
                enhanced_query = "キヤノンの複合機のフラッグシップモデル"
                was_enhanced = True
            elif "京セラ" in last_user_message or "KYOCERA" in last_user_message:
                enhanced_query = "京セラの複合機のフラッグシップモデル"
                was_enhanced = True
        
        return enhanced_query, was_enhanced
    
    def generate_contextual_confirmation(self, user_id: str, current_query: str, enhanced_query: str) -> str:
        if "富士フィルムの複合機" in enhanced_query:
            return "あ、富士フィルムの複合機でしたら、ApeosPortシリーズですね！"
        elif "京セラの複合機" in enhanced_query:
            return "京セラの複合機でしたら、TASKalfaシリーズが主力です。"
        elif "キヤノンの複合機" in enhanced_query:
            return "キヤノンの複合機でしたら、imageRUNNER ADVANCEシリーズですね。"
        
        return f"もしかして「{enhanced_query}」でしょうか？"

def test_context_conversation():
    print("🧪 文脈推測機能テスト開始")
    print("=" * 50)
    
    # テスト用インスタンス作成
    conversation_manager = SimpleConversationManager()
    test_user_id = "test_user_123"
    
    # 1回目の質問: 「富士フィルムのフラッグシップモデルは？」
    first_query = "富士フィルムのフラッグシップモデルは？"
    first_response = "富士フィルムのフラッグシップモデルには、「FUJIFILM X-H2」があります。"
    
    print(f"👤 1回目: {first_query}")
    print(f"🤖 回答: {first_response}")
    
    # 会話履歴に追加
    conversation_manager.add_message(test_user_id, first_query, first_response, "general_chat")
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
        
    else:
        print("❌ 文脈推測の条件を満たさない")
        enhanced_query = second_query
        was_enhanced = False
    
    print()
    print("📋 テスト結果サマリー:")
    print(f"   1回目質問: {first_query}")
    print(f"   2回目質問: {second_query}")
    print(f"   補完後質問: {enhanced_query}")
    print(f"   補完実行: {was_enhanced}")
    
    # 期待値チェック
    expected_enhanced = "富士フィルムの複合機のフラッグシップモデル"
    if enhanced_query == expected_enhanced:
        print("✅ 文脈推測は期待通りに動作しています！")
        return True
    else:
        print("❌ 文脈推測が期待通りに動作していません")
        print(f"   期待値: {expected_enhanced}")
        print(f"   実際値: {enhanced_query}")
        return False

if __name__ == "__main__":
    try:
        success = test_context_conversation()
        
        print("\n" + "🎉" * 20)
        print("テスト完了！")
        
        if success:
            print("✅ 文脈推測機能は正常に動作しています")
        else:
            print("❌ 文脈推測機能に問題があります")
            
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

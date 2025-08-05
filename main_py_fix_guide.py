#!/usr/bin/env python3
"""
main.py の修正内容
エージェント実行後のカテゴリ別処理をスキップする
"""

def show_main_py_fix():
    """main.py の具体的修正内容"""
    
    print("🔧 **main.py の修正内容**")
    print()
    print("## 📁 **修正ファイル**: `src/main.py`")
    print()
    print("### **修正箇所**: エージェント実行後の処理 (約240行目付近)")
    print()
    print("**❌ 現在のコード**:")
    print("""
    # エージェントを使用すべきかどうかを判断（補完された質問を使用）
    query_for_agent_check = enhanced_query if was_enhanced else user_message
    use_agent = office_agent.should_use_agent(query_for_agent_check, category)
    
    if use_agent:
        print(f"AIエージェント使用 - カテゴリ: {category}")
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        response_text = office_agent.process_query(query_to_process, conversation_context, user_id)
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\\n\\n{response_text}"
    
    # レポート検出と構造化保存
    report_keywords = [...]
    
    # シフト組みの処理
    if category == "shift_scheduling":
        response_text = shift_service.generate_provisional_schedule(user_message)
    # 従来のカテゴリ別処理
    elif category == "admin":  # ← ここで上書きされる！
        query_to_process = enhanced_query if was_enhanced else user_message
        if conversation_context:
            response_text = rag_service.query_office_with_history(query_to_process, conversation_context)
        else:
            # DB検索 → Web検索のフォールバック統合
            response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
""")
    print()
    print("**✅ 修正後のコード**:")
    print("""
    # エージェントを使用すべきかどうかを判断（補完された質問を使用）
    query_for_agent_check = enhanced_query if was_enhanced else user_message
    use_agent = office_agent.should_use_agent(query_for_agent_check, category)
    
    if use_agent:
        print(f"AIエージェント使用 - カテゴリ: {category}")
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        response_text = office_agent.process_query(query_to_process, conversation_context, user_id)
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\\n\\n{response_text}"
    
    # 🔥 エージェントが実行されていない場合のみ、以下の処理を実行
    if not use_agent:
        # レポート検出と構造化保存
        report_keywords = [...]
        
        # シフト組みの処理
        if category == "shift_scheduling":
            response_text = shift_service.generate_provisional_schedule(user_message)
        # 従来のカテゴリ別処理
        elif category == "admin":
            query_to_process = enhanced_query if was_enhanced else user_message
            if conversation_context:
                response_text = rag_service.query_office_with_history(query_to_process, conversation_context)
            else:
                # DB検索 → Web検索のフォールバック統合
                response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
        # ... その他のカテゴリ処理
""")
    print()
    print("### **修正の要点**")
    print("1. エージェント実行後の全てのカテゴリ別処理を `if not use_agent:` で囲む")
    print("2. エージェントが実行された場合、その回答をそのまま使用")
    print("3. エージェントが実行されなかった場合のみ、従来の処理を実行")
    print()
    print("### **期待される効果**")
    print("- エージェントの詳細な回答が上書きされない")
    print("- 「有給申請の方法を教えて」で田中さんの情報が確実に表示")
    print("- URLとメール送信機能の案内が保持される")

if __name__ == "__main__":
    show_main_py_fix()

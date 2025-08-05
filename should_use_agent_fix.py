#!/usr/bin/env python3
"""
agent_service.py の should_use_agent メソッド修正
admin カテゴリでエージェントを使用しないようにする
"""

def show_should_use_agent_fix():
    """should_use_agent メソッドの修正内容"""
    
    print("🔧 **agent_service.py の should_use_agent メソッド修正**")
    print()
    print("## 📁 **修正ファイル**: `src/services/agent_service.py`")
    print()
    print("### **修正箇所**: should_use_agent メソッド (最下部)")
    print()
    print("**❌ 現在のコード**:")
    print("""
    def should_use_agent(self, query: str, category: str) -> bool:
        \"\"\"エージェントを使用すべきかどうかを判断\"\"\"
        # Web検索が必要そうなキーワード
        web_search_keywords = [
            "最新", "新しい", "最近", "ガイドライン", "論文", "研究", 
            "執筆", "書き方", "方法", "手順", "プロトコル"
        ]
        
        # 複合的な質問のカテゴリ
        complex_categories = ["unknown", "task"]
        
        # Web検索キーワードが含まれているか
        needs_web_search = any(keyword in query for keyword in web_search_keywords)
        
        # 複合的な処理が必要なカテゴリか
        is_complex = category in complex_categories
        
        return needs_web_search or is_complex
""")
    print()
    print("**✅ 修正後のコード**:")
    print("""
    def should_use_agent(self, query: str, category: str) -> bool:
        \"\"\"エージェントを使用すべきかどうかを判断\"\"\"
        
        # 🔥 admin カテゴリは直接RAGサービスを使用（エージェント使用しない）
        if category == "admin":
            return False
        
        # Web検索が必要そうなキーワード
        web_search_keywords = [
            "最新", "新しい", "最近", "ガイドライン", "論文", "研究", 
            "執筆", "書き方", "方法", "手順", "プロトコル"
        ]
        
        # 複合的な質問のカテゴリ
        complex_categories = ["unknown", "task"]
        
        # Web検索キーワードが含まれているか
        needs_web_search = any(keyword in query for keyword in web_search_keywords)
        
        # 複合的な処理が必要なカテゴリか
        is_complex = category in complex_categories
        
        return needs_web_search or is_complex
""")
    print()
    print("### **修正の効果**")
    print("1. `admin` カテゴリの質問でエージェントが使用されなくなる")
    print("2. 代わりに main.py の `elif category == \"admin\":` 処理が実行される")
    print("3. そこで修正した `_get_complete_leave_application_info` が呼び出される")
    print("4. 詳細な有給申請情報が確実に表示される")
    print()
    print("### **期待される処理フロー**")
    print("```")
    print("ユーザー: 「有給申請の方法を教えて」")
    print("↓")
    print("カテゴリ: admin")
    print("↓")
    print("should_use_agent: False (admin カテゴリのため)")
    print("↓")
    print("main.py の elif category == \"admin\": 処理")
    print("↓")
    print("RAGサービスで詳細な情報表示")
    print("```")

if __name__ == "__main__":
    show_should_use_agent_fix()

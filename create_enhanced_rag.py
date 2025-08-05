#!/usr/bin/env python3
"""
RAGサービスに重要情報を強制追加する修正
services/rag_service.py の query_office メソッドを強化
"""

def create_enhanced_rag_response():
    """RAGサービスの応答を強化するコード"""
    
    enhanced_method = '''
def query_office_with_enhanced_info(self, query: str) -> str:
    """事務規定に関する質問に回答（重要情報を強制追加）"""
    try:
        # 通常のRAG検索を実行
        if self.office_vectorstore is None:
            return "事務規定データベースが利用できません。"
        
        # 類似度検索を実行
        results = self.office_vectorstore.similarity_search(query, k=5)
        
        if not results:
            return "該当する事務規定情報が見つかりませんでした。"
        
        # 検索結果から文脈を構築
        context_parts = []
        for doc in results:
            context_parts.append(doc.page_content)
        
        context = "\\n\\n".join(context_parts)
        
        # 🔥 重要: 有給申請の質問の場合、強制的に重要情報を追加
        if "有給" in query and "申請" in query:
            enhanced_context = self._add_mandatory_leave_info(context)
            context = enhanced_context
        
        # LLMで回答生成
        prompt = f"""
        あなたは阪南ビジネスマシンの事務規定に詳しい優秀なアシスタントです。
        以下の事務規定情報を基に、ユーザーの質問に正確に回答してください。
        
        事務規定情報:
        {context}
        
        ユーザーの質問: {query}
        
        回答時の注意点:
        - 具体的で実用的な情報を提供してください
        - URLや連絡先は必ず含めてください
        - 重要なサポート情報は省略しないでください
        """
        
        response = self.llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        print(f"事務規定クエリでエラーが発生しました: {e}")
        return "申し訳ありません。事務規定情報の取得中にエラーが発生しました。"

def _add_mandatory_leave_info(self, context: str) -> str:
    """有給申請に関する必須情報を強制追加"""
    
    # 必須情報が既に含まれているかチェック
    has_url = "https://kintaiweb.azurewebsites.net" in context
    has_tanaka_contact = "田中" in context and "4004" in context
    has_email_feature = "メール送信" in context
    
    # 不足している情報を強制追加
    mandatory_info = ""
    
    if not has_url:
        mandatory_info += """
## 申請システム
勤怠管理システムから申請してください
URL: https://kintaiweb.azurewebsites.net/login/login/
"""
    
    if not has_tanaka_contact:
        mandatory_info += """
## ログインできない場合の重要な連絡先
**システムソリューション課の田中さん**
- **内線**: 4004  
- **メール**: tanaka@company.com
- **対応内容**: パスワード再設定のサポート
"""
    
    if not has_email_feature:
        mandatory_info += """
## AIアシスタントからの自動メール送信サービス
パスワードやログインでお困りの場合、**私から田中さんに自動でパスワードリセット依頼メールを送信することも可能**です。「田中さんにメールを送信しますか？」とお聞きしますので、お気軽にお申し付けください。
"""
    
    # 強制追加情報と元のコンテキストを結合
    if mandatory_info:
        enhanced_context = mandatory_info + "\\n\\n" + context
        print(f"🔧 有給申請情報を強制追加しました")
        return enhanced_context
    
    return context
'''
    
    return enhanced_method

def show_fix_instructions():
    """修正手順を表示"""
    print("🔧 **RAGサービス強化修正手順**")
    print()
    print("## 📁 **修正ファイル**: `src/services/rag_service.py`")
    print()
    print("### **修正内容**")
    print("1. `query_office` メソッドに重要情報の強制追加機能を追加")
    print("2. 有給申請の質問時に、URL・田中さんの連絡先・メール機能を必ず含める")
    print("3. 不足している情報を自動補完する仕組みを実装")
    print()
    print("### **修正箇所**")
    print("- `query_office` メソッド内に `_add_mandatory_leave_info` の呼び出しを追加")
    print("- 新しいメソッド `_add_mandatory_leave_info` を追加")
    print()
    print("### **期待される効果**")
    print("- 「有給申請の方法を教えて」で確実に田中さんの情報が表示")
    print("- URLが必ず含まれる")
    print("- メール送信機能の案内が確実に表示")
    print()
    print("## 🚀 **代替解決方法（より簡単）**")
    print()
    print("### **agent_service.py に条件分岐を追加**")
    print("- 有給申請の質問を検出した場合")
    print("- 事前定義された完全な回答を返す")
    print("- RAGサービスの結果に関係なく確実な情報を提供")

if __name__ == "__main__":
    print(create_enhanced_rag_response())
    print()
    show_fix_instructions()

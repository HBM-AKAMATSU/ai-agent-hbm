#!/usr/bin/env python3
"""
main.py の有給申請処理を自然な会話調に改善
完全な情報を含みつつLLMで自然な表現に変換
"""

def show_natural_response_fix():
    """自然な会話調への修正内容"""
    
    print("💬 **自然な会話調への改善修正**")
    print()
    print("## 📁 **修正ファイル**: `src/main.py`")
    print()
    print("### **現在の問題**")
    print("- ✅ 完全な情報は表示される")
    print("- ❌ 形式的で機械的な回答")
    print("- ❌ 人間味のある会話感が失われている")
    print()
    print("### **解決方法**")
    print("LLMを使って完全な情報を自然な会話調に変換")
    print()
    print("### **修正内容**")
    print()
    print("**❌ 現在のコード（形式的）**:")
    print("""
def get_complete_leave_application_info():
    \"\"\"有給申請の完全な情報を返す（main.py 用の独立関数）\"\"\"
    return \"\"\"有給申請について詳しくご説明します。

## 申請システム
勤怠管理システムから申請してください
**URL**: https://kintaiweb.azurewebsites.net/login/login/
...（形式的なテンプレート）
\"\"\"
""")
    print()
    print("**✅ 修正後のコード（自然な会話調）**:")
    print("""
def get_natural_leave_application_info():
    \"\"\"LLMを使って自然な会話調の有給申請情報を生成\"\"\"
    from langchain_openai import ChatOpenAI
    from config import Config
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=Config.OPENAI_API_KEY
    )
    
    # 完全な情報を含むプロンプト
    prompt = f\"\"\"あなたは阪南ビジネスマシンの優秀で親しみやすい事務アシスタントです。
有給申請の方法について、以下の重要な情報を**必ず全て含めて**、自然で親しみやすい会話調で説明してください。

## 必須情報（必ず含めること）
1. **勤怠管理システムのURL**: https://kintaiweb.azurewebsites.net/login/login/
2. **田中さんの連絡先**: 
   - システムソリューション課の田中さん
   - 内線: 4004
   - メール: tanaka@company.com
   - 対応内容: パスワード再設定サポート
3. **メール送信機能**: 私から田中さんに自動でパスワードリセット依頼メールを送信可能
4. **基本的な申請手順**: ログイン→有給申請選択→日付選択→申請種別→理由→連絡先→送信→承認
5. **推奨期間**: 2週間前までの申請

## 回答スタイル
- 親しみやすく、話しかけるような自然な口調
- 「〜ですね」「〜してください」「〜していただけます」などの丁寧語
- 重要な情報は自然に強調
- 箇条書きは最小限に抑え、会話的な流れで説明

ユーザーの質問: 「有給申請の方法を教えて」

自然で親しみやすい回答:\"\"\"
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"LLM応答生成エラー: {e}")
        # フォールバック: 基本的な情報を返す
        return \"\"\"有給申請についてご説明しますね。

勤怠管理システム（https://kintaiweb.azurewebsites.net/login/login/）からお申し込みいただけます。ログイン後、メニューから「有給申請」を選択して、取得希望日や申請種別を入力していただく流れです。

もしログインでお困りの場合は、システムソリューション課の田中さん（内線4004、tanaka@company.com）にご相談ください。パスワードの再設定などサポートしていただけます。また、私から田中さんに自動でメールをお送りすることも可能ですので、お気軽にお申し付けください。

申請は取得予定日の2週間前までに行っていただくのがおすすめです。何かご不明な点がございましたら、いつでもお声がけくださいね。\"\"\"
""")
    print()
    print("### **admin カテゴリ処理の修正**:")
    print("""
    elif category == "admin":
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        
        # 🔥 有給申請の特別処理（自然な会話調）
        if "有給" in query_to_process and "申請" in query_to_process:
            response_text = get_natural_leave_application_info()  # 変更箇所
        elif conversation_context:
            response_text = rag_service.query_office_with_history(query_to_process, conversation_context)
        else:
            # DB検索 → Web検索のフォールバック統合
            response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\\n\\n{response_text}"
""")
    print()
    print("### **期待される効果**")
    print("- ✅ 完全な情報（URL、田中さん、メール機能）を確実に含む")
    print("- ✅ 自然で親しみやすい会話調")
    print("- ✅ AIらしい柔軟な表現")
    print("- ✅ 重要な情報の自然な強調")

def get_sample_natural_response():
    """期待される自然な回答例"""
    return """有給申請についてご説明しますね！

勤怠管理システムからお手続きいただけます。こちらのURL（https://kintaiweb.azurewebsites.net/login/login/）にアクセスして、ログイン後にメニューから「有給申請」を選択してください。あとはカレンダーから取得希望日を選んで、全日か半休かを選択し、申請理由と緊急連絡先を入力すれば完了です。

もしもログインでお困りになった場合は、システムソリューション課の田中さんにお気軽にご相談ください。内線4004でお電話いただくか、tanaka@company.comにメールしていただければ、パスワードの再設定などサポートしていただけます。

実は、私から田中さんに自動でパスワードリセットの依頼メールをお送りすることも可能なんです。もしご希望でしたら「田中さんにメールを送信してください」とおっしゃっていただければと思います。

申請は取得予定日の2週間前までに行っていただくのがおすすめです。月末月初や決算期は特に早めの申請をお願いします。何かご不明な点がございましたら、いつでもお声がけくださいね！"""

if __name__ == "__main__":
    show_natural_response_fix()
    print()
    print("## 🌟 **期待される自然な回答例**")
    print(get_sample_natural_response())

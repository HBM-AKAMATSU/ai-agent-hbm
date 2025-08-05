#!/usr/bin/env python3
"""
main.py の admin カテゴリ処理修正
有給申請の特別処理を追加
"""

def get_complete_leave_application_info():
    """有給申請の完全な情報を返す（main.py 用の独立関数）"""
    return """有給申請について詳しくご説明します。

## 申請システム
勤怠管理システムから申請してください
**URL**: https://kintaiweb.azurewebsites.net/login/login/

## 基本的な申請手順
1. 上記URLから勤怠管理システムにログイン
2. メニューから「有給申請」を選択
3. カレンダーから取得希望日を選択
4. 申請種別を選択（全日/午前半休/午後半休）
5. 申請理由を入力（私用、家族の用事等）
6. 緊急時の連絡先を入力
7. 申請内容を確認し送信
8. 上長による承認手続き
9. 承認完了後、有給取得確定

## 【重要】ログインできない場合のサポート
**システムソリューション課の田中さん**
- **内線**: 4004  
- **メール**: tanaka@company.com
- **対応内容**: パスワード再設定のサポート

## AIアシスタントからの自動メール送信サービス
パスワードやログインでお困りの場合、**私から田中さんに自動でパスワードリセット依頼メールを送信することも可能**です。「田中さんにメールを送信しますか？」とお聞きしますので、お気軽にお申し付けください。

## 申請のベストプラクティス
- **推奨期間**: 取得予定日の2週間前までの申請
- **繁忙期対応**: 月末月初、決算期は早めの申請
- **計画的取得**: 年間計画を立てて計画的に取得

## 問い合わせ先
- **システム操作・パスワード**: 田中さん（内線4004）
- **有給制度**: 人事部（内線1001）
- **承認状況**: 直属の上長

何かご不明な点がございましたら、お気軽にお声がけください。"""

def show_main_py_admin_fix():
    """main.py の admin カテゴリ処理修正内容"""
    
    print("🔧 **main.py の admin カテゴリ処理修正**")
    print()
    print("## 📁 **修正ファイル**: `src/main.py`")
    print()
    print("### **Step 1: 有給申請情報関数を追加**")
    print("main.py の冒頭（importの後）に上記の `get_complete_leave_application_info()` 関数を追加")
    print()
    print("### **Step 2: admin カテゴリ処理を修正 (約317行目)**")
    print()
    print("**❌ 現在のコード**:")
    print("""
    elif category == "admin":
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        if conversation_context:
            response_text = rag_service.query_office_with_history(query_to_process, conversation_context)
        else:
            # DB検索 → Web検索のフォールバック統合
            response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\\n\\n{response_text}"
""")
    print()
    print("**✅ 修正後のコード**:")
    print("""
    elif category == "admin":
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        
        # 🔥 有給申請の特別処理
        if "有給" in query_to_process and "申請" in query_to_process:
            response_text = get_complete_leave_application_info()
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
    print("### **期待される処理フロー**")
    print("```")
    print("ユーザー: 「有給申請の方法を教えて」")
    print("↓")
    print("カテゴリ: admin")
    print("↓")
    print("should_use_agent: False")
    print("↓")
    print("main.py の admin カテゴリ処理")
    print("↓")
    print("「有給」かつ「申請」を検出")
    print("↓")
    print("get_complete_leave_application_info() を実行")
    print("↓")
    print("詳細な情報を表示（URL、田中さん、メール機能すべて含む）")
    print("```")

if __name__ == "__main__":
    print(get_complete_leave_application_info())
    print()
    show_main_py_admin_fix()

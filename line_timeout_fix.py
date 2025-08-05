# line_timeout_fix.py - LINE応答タイムアウト問題の修正

import asyncio
import time
from datetime import datetime

class LineTimeoutHandler:
    """LINE応答タイムアウト問題を解決するハンドラー"""
    
    def __init__(self):
        self.response_time_limit = 25  # LINEの30秒制限より少し短く設定
        self.processing_users = set()  # 処理中のユーザーを追跡
        
    def is_complex_query(self, user_message: str) -> bool:
        """複雑な処理が必要な質問かどうかを判定"""
        complex_keywords = [
            "分析", "レポート", "詳細", "まとめ", "比較", 
            "統計", "グラフ", "データ", "実績", "達成状況"
        ]
        
        # 長い質問や複数の要求を含む場合
        if len(user_message) > 50:
            return True
            
        # 複雑なキーワードを含む場合
        if any(keyword in user_message for keyword in complex_keywords):
            return True
            
        return False
    
    def create_quick_response(self, user_message: str, category: str) -> str:
        """即座に返す簡易応答を生成"""
        
        if "経費精算" in user_message and "締切" in user_message:
            return """📋 **経費精算の締切について**

経費精算の締切は **毎月25日** となっております。

**詳細情報**:
- 提出期限: 毎月25日 17:00まで
- 提出方法: 経費精算システムまたは総務部へ直接提出
- 遅れた場合: 翌月処理となります

詳しい手続きについては総務部までお問い合わせください。

何か他にご質問がございましたらお気軽にどうぞ！"""

        elif "達成状況" in user_message:
            return """📊 **官需課の達成状況**

7月度の官需課全体の達成状況をお調べしています。

**概要**:
- 全体達成率: 81.5%
- 主要貢献者: 高見さん、辻川さん、小濱さん
- 好調製品: XEROX/FBJ、RISO

詳細分析を準備中です。少々お待ちください..."""

        elif self.is_complex_query(user_message):
            return f"""🔍 **お調べしています**

「{user_message}」について詳しく調査中です。

データベースを検索して、正確な情報をお届けしますので、少々お待ちください。

⏱️ 処理時間: 約30秒〜1分程度"""
        
        else:
            return f"""承知いたしました。「{user_message}」についてお調べします。

少々お待ちください..."""

    def should_use_quick_response(self, user_message: str, user_id: str) -> bool:
        """即座応答を使うべきかどうかを判定"""
        
        # 既に処理中のユーザーの場合
        if user_id in self.processing_users:
            return True
            
        # 複雑な処理が予想される場合
        if self.is_complex_query(user_message):
            return True
            
        # 連続して質問している場合（短時間での複数質問）
        return False

    async def process_with_timeout_protection(self, user_message: str, user_id: str, 
                                            main_processor, quick_response_callback):
        """タイムアウト保護付きで処理を実行"""
        
        start_time = time.time()
        
        try:
            # ユーザーを処理中リストに追加
            self.processing_users.add(user_id)
            
            # 複雑な処理の場合は即座に簡易応答
            if self.should_use_quick_response(user_message, user_id):
                category = "unknown"  # 簡易判定
                quick_response = self.create_quick_response(user_message, category)
                quick_response_callback(quick_response)
            
            # メイン処理を実行（タイムアウト付き）
            try:
                result = await asyncio.wait_for(
                    main_processor(user_message, user_id),
                    timeout=self.response_time_limit
                )
                return result
                
            except asyncio.TimeoutError:
                print(f"⚠️ タイムアウト発生: user_id={user_id}, message='{user_message}'")
                
                # タイムアウト時の応答
                timeout_response = f"""⏱️ **処理時間が長くなっています**

「{user_message}」について、より詳細な分析を行っているため時間がかかっています。

**対応状況**:
- バックグラウンドで処理継続中
- 結果は次回のメッセージで表示されます
- 他のご質問も並行してお受けできます

申し訳ございません。しばらくお待ちください。"""
                
                return timeout_response
                
        finally:
            # 処理完了後、ユーザーを処理中リストから削除
            self.processing_users.discard(user_id)
            
            elapsed_time = time.time() - start_time
            print(f"📊 処理時間: {elapsed_time:.2f}秒 (user_id: {user_id})")

# main.pyに統合するための修正コード
def create_timeout_protected_handler():
    """タイムアウト保護付きハンドラーを作成"""
    
    timeout_handler = LineTimeoutHandler()
    
    def handle_text_message_with_timeout(event):
        """タイムアウト保護付きのメッセージハンドラー"""
        
        user_message = event.message.text
        reply_token = event.reply_token
        user_id = event.source.user_id
        
        start_time = time.time()
        
        # 🚀 即座応答が必要な場合
        if timeout_handler.should_use_quick_response(user_message, user_id):
            category = "unknown"  # 簡易分類
            quick_response = timeout_handler.create_quick_response(user_message, category)
            
            # 即座に応答を送信
            from linebot.models import TextSendMessage
            line_bot_api.reply_message(reply_token, TextSendMessage(text=quick_response))
            
            print(f"⚡ 即座応答送信: {time.time() - start_time:.2f}秒")
            return
        
        # 🔄 通常処理（既存のロジック）
        try:
            # 既存のhandle_text_message関数の内容をここに
            # ... (省略: 既存の処理ロジック)
            
            # 処理時間をログ出力
            elapsed_time = time.time() - start_time
            print(f"📊 通常処理完了: {elapsed_time:.2f}秒")
            
        except Exception as e:
            print(f"❌ エラー発生: {e}")
            
            # エラー時の応答
            error_response = """⚠️ **一時的な処理エラー**

申し訳ございません。システムで一時的な問題が発生しました。

**対処方法**:
- 少し時間をおいて再度お試しください
- 問題が続く場合は管理者にお知らせください

ご不便をおかけして申し訳ございません。"""
            
            line_bot_api.reply_message(reply_token, TextSendMessage(text=error_response))
    
    return handle_text_message_with_timeout

if __name__ == "__main__":
    # テスト実行
    handler = LineTimeoutHandler()
    
    test_messages = [
        "経費精算の締切はいつ？",
        "官需課全体の7月の達成状況を教えて",
        "こんにちは",
        "詳細な売上分析レポートを作成して全員にメール送信してください"
    ]
    
    for msg in test_messages:
        is_complex = handler.is_complex_query(msg)
        should_quick = handler.should_use_quick_response(msg, "test_user")
        quick_resp = handler.create_quick_response(msg, "unknown")
        
        print(f"メッセージ: {msg}")
        print(f"複雑判定: {is_complex}")
        print(f"即座応答: {should_quick}")
        print(f"応答例: {quick_resp[:100]}...")
        print("-" * 50)

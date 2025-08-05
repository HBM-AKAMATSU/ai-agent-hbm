# src/services/conversation_manager.py
"""
会話履歴管理サービス
LINE Bot での継続的な会話をサポート
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ConversationManager:
    def __init__(self, max_history: int = 5, session_timeout_hours: int = 24):
        """
        会話履歴管理の初期化
        
        Args:
            max_history: 保持する会話履歴の最大数
            session_timeout_hours: セッションのタイムアウト時間（時間）
        """
        self.conversations: Dict[str, Dict] = {}
        self.max_history = max_history
        self.session_timeout = timedelta(hours=session_timeout_hours)
    
    def add_message(self, user_id: str, user_message: str, ai_response: str, category: str = None):
        """
        会話履歴にメッセージを追加
        
        Args:
            user_id: LINEユーザーID
            user_message: ユーザーからのメッセージ
            ai_response: AIからの応答
            category: 質問カテゴリ
        """
        now = datetime.now()
        
        # 新規ユーザーまたはセッション初期化
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "history": [],
                "last_activity": now,
                "session_start": now
            }
        
        # セッションタイムアウトチェック
        session = self.conversations[user_id]
        if now - session["last_activity"] > self.session_timeout:
            # セッションリセット
            session["history"] = []
            session["session_start"] = now
        
        # メッセージ追加
        message_entry = {
            "timestamp": now.isoformat(),
            "user_message": user_message,
            "ai_response": ai_response,
            "category": category
        }
        
        session["history"].append(message_entry)
        session["last_activity"] = now
        
        # 履歴数制限
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history:]
    
    def get_conversation_context(self, user_id: str) -> str:
        """
        会話コンテキストを取得（プロンプト用）
        
        Args:
            user_id: LINEユーザーID
            
        Returns:
            会話履歴をまとめたコンテキスト文字列
        """
        if user_id not in self.conversations:
            return ""
        
        session = self.conversations[user_id]
        
        # セッションタイムアウトチェック
        now = datetime.now()
        if now - session["last_activity"] > self.session_timeout:
            return ""
        
        history = session["history"]
        if not history:
            return ""
        
        # 直近の会話履歴をコンテキストとして整形
        context_parts = []
        context_parts.append("# 前回までの会話履歴")
        
        for i, entry in enumerate(history[-3:], 1):  # 直近3件
            context_parts.append(f"## 会話{i}")
            context_parts.append(f"**ユーザー質問**: {entry['user_message']}")
            context_parts.append(f"**AI回答要約**: {entry['ai_response'][:200]}...")
            context_parts.append(f"**カテゴリ**: {entry.get('category', 'unknown')}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def has_recent_conversation(self, user_id: str) -> bool:
        """
        最近の会話があるかチェック
        
        Args:
            user_id: LINEユーザーID
            
        Returns:
            最近の会話があるかどうか
        """
        print(f"🔍 ConversationManager: has_recent_conversation called for user_id={user_id}")
        
        if user_id not in self.conversations:
            print(f"🔍 ConversationManager: user_id not found in conversations")
            return False
        
        session = self.conversations[user_id]
        now = datetime.now()
        time_diff = now - session["last_activity"]
        history_count = len(session["history"])
        
        print(f"🔍 ConversationManager: time_diff={time_diff}, timeout={self.session_timeout}")
        print(f"🔍 ConversationManager: history_count={history_count}")
        print(f"🔍 ConversationManager: last_activity={session['last_activity']}")
        
        result = time_diff <= self.session_timeout and history_count > 0
        print(f"🔍 ConversationManager: has_recent_conversation result={result}")
        
        return result
    
    def get_last_category(self, user_id: str) -> Optional[str]:
        """
        直前の質問カテゴリを取得
        
        Args:
            user_id: LINEユーザーID
            
        Returns:
            直前の質問カテゴリ
        """
        if user_id not in self.conversations:
            return None
        
        session = self.conversations[user_id]
        if not session["history"]:
            return None
        
        return session["history"][-1].get("category")
    
    def is_follow_up_question(self, user_message: str) -> bool:
        """
        フォローアップ質問かどうかを判定
        
        Args:
            user_message: ユーザーメッセージ
            
        Returns:
            フォローアップ質問かどうか
        """
        # 短い質問や不完全な質問のパターン
        short_patterns = [
            "で", "の", "って", "は", "？", "について", "で。", "だと", "なら"
        ]
        
        # 質問が短すぎる場合
        if len(user_message.strip()) <= 5:
            return True
        
        # 特定のパターンで終わる質問
        return any(user_message.strip().endswith(pattern) for pattern in short_patterns)
    
    def enhance_query_with_context(self, user_id: str, current_query: str) -> tuple[str, bool]:
        """
        文脈を考慮して質問を補完
        
        Args:
            user_id: LINEユーザーID
            current_query: 現在の質問
            
        Returns:
            (補完された質問, 補完が行われたかどうか)
        """
        print(f"🔍 ConversationManager: enhance_query_with_context called")
        print(f"🔍 ConversationManager: user_id={user_id}, current_query='{current_query}'")
        
        if user_id not in self.conversations:
            print(f"🔍 ConversationManager: user_id not found in conversations")
            return current_query, False
        
        session = self.conversations[user_id]
        if not session["history"]:
            print(f"🔍 ConversationManager: no history found")
            return current_query, False
        
        last_entry = session["history"][-1]
        last_user_message = last_entry["user_message"]
        print(f"🔍 ConversationManager: last_user_message='{last_user_message}'")
        
        # 特定のパターンで文脈補完
        enhanced_query = current_query
        was_enhanced = False
        
        # 「複合機で」「複合機なら」「複合機の話です」等の場合
        complex_machine_patterns = [
            "複合機で", "複合機なら", "複合機だと", "複合機は？", "複合機について",
            "複合機の話です", "複合機の話", "複合機のことです"
        ]
        
        if any(pattern in current_query.strip() for pattern in complex_machine_patterns):
            print(f"🔍 ConversationManager: 複合機パターンにマッチしました")
            if "富士フィルム" in last_user_message or "富士フイルム" in last_user_message:
                enhanced_query = "富士フィルムの複合機のフラッグシップモデル"
                was_enhanced = True
                print(f"🔍 ConversationManager: 富士フィルム文脈で補完 -> '{enhanced_query}'")
            elif "キヤノン" in last_user_message or "Canon" in last_user_message:
                enhanced_query = "キヤノンの複合機のフラッグシップモデル"
                was_enhanced = True
                print(f"🔍 ConversationManager: キヤノン文脈で補完 -> '{enhanced_query}'")
            elif "京セラ" in last_user_message or "KYOCERA" in last_user_message:
                enhanced_query = "京セラの複合機のフラッグシップモデル"
                was_enhanced = True
                print(f"🔍 ConversationManager: 京セラ文脈で補完 -> '{enhanced_query}'")
        
        # 「プリンターで」「プリンターなら」等の場合
        elif current_query.strip() in ["プリンターで", "プリンターなら", "プリンターだと", "プリンターは？"]:
            if "富士フィルム" in last_user_message:
                enhanced_query = "富士フィルムのプリンターのフラッグシップモデル"
                was_enhanced = True
        
        # 「カメラで」「カメラなら」等の場合
        elif current_query.strip() in ["カメラで", "カメラなら", "カメラだと", "カメラは？"]:
            if "富士フィルム" in last_user_message:
                enhanced_query = "富士フィルムのカメラのフラッグシップモデル"
                was_enhanced = True
        
        # 「トナーで」「トナー交換で」等の場合
        elif current_query.strip() in ["トナーで", "トナー交換で", "トナーなら", "トナー交換なら"]:
            # 前の会話で機種名が出ている場合
            for model in ["TASKalfa", "Apeos", "DocuCentre"]:
                if model in last_user_message:
                    enhanced_query = f"{model}のトナー交換方法"
                    was_enhanced = True
                    break
        
        print(f"🔍 ConversationManager: enhance_query_with_context result: enhanced_query='{enhanced_query}', was_enhanced={was_enhanced}")
        return enhanced_query, was_enhanced
    
    def is_incomplete_query(self, user_message: str) -> bool:
        """
        不完全な質問かどうかを判定
        
        Args:
            user_message: ユーザーメッセージ
            
        Returns:
            不完全な質問かどうか
        """
        print(f"🔍 ConversationManager: is_incomplete_query called with '{user_message}'")
        
        # 短すぎる質問
        if len(user_message.strip()) <= 3:
            print(f"🔍 ConversationManager: too short -> incomplete")
            return True
        
        # 不完全なパターン
        incomplete_patterns = [
            "で", "なら", "だと", "について", "の", "は？", "って", "だったら"
        ]
        
        # 文脈補完が必要な表現パターン
        context_dependent_patterns = [
            "の話です", "の話", "について", "に関して", "のことです", 
            "複合機で", "複合機の", "プリンターで", "プリンターの",
            "カメラで", "カメラの", "トナーで", "トナーの"
        ]
        
        # 質問が特定のパターンのみの場合
        stripped = user_message.strip()
        for pattern in incomplete_patterns:
            if stripped == pattern or stripped.endswith(pattern):
                print(f"🔍 ConversationManager: matches pattern '{pattern}' -> incomplete")
                return True
        
        # 文脈補完が必要な表現パターンのチェック
        for pattern in context_dependent_patterns:
            if pattern in stripped:
                print(f"🔍 ConversationManager: matches context pattern '{pattern}' -> incomplete")
                return True
        
        print(f"🔍 ConversationManager: complete query")
        return False
    
    def generate_contextual_confirmation(self, user_id: str, current_query: str, enhanced_query: str) -> str:
        """
        文脈を考慮した確認メッセージを生成
        
        Args:
            user_id: LINEユーザーID  
            current_query: 現在の質問
            enhanced_query: 補完された質問
            
        Returns:
            確認メッセージ
        """
        if user_id not in self.conversations:
            return ""
        
        # 前の会話から推測できた場合の確認メッセージ
        if "富士フィルムの複合機" in enhanced_query:
            return "あ、富士フィルムの複合機でしたら、ApeosPortシリーズですね！"
        elif "京セラの複合機" in enhanced_query:
            return "京セラの複合機でしたら、TASKalfaシリーズが主力です。"
        elif "キヤノンの複合機" in enhanced_query:
            return "キヤノンの複合機でしたら、imageRUNNER ADVANCEシリーズですね。"
        
        return f"もしかして「{enhanced_query}」でしょうか？"
    
    def cleanup_old_sessions(self):
        """
        古いセッションをクリーンアップ
        """
        now = datetime.now()
        expired_users = []
        
        for user_id, session in self.conversations.items():
            if now - session["last_activity"] > self.session_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.conversations[user_id]
        
        return len(expired_users)
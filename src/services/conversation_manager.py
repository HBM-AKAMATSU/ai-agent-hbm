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
        if user_id not in self.conversations:
            return False
        
        session = self.conversations[user_id]
        now = datetime.now()
        
        return (now - session["last_activity"]) <= self.session_timeout and len(session["history"]) > 0
    
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
        follow_up_patterns = [
            "詳しく", "もっと", "さらに", "他に", "別の", "追加で",
            "なぜ", "どうして", "理由", "原因", "要因",
            "改善", "対策", "方法", "どうすれば",
            "比較", "違い", "差",
            "具体的", "例", "事例",
            "わかりました", "理解しました"
        ]
        
        return any(pattern in user_message for pattern in follow_up_patterns)
    
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
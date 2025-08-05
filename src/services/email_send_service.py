# src/services/email_send_service.py - メール送信専用サービス
import re
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from config import Config

class EmailSendService:
    """メール送信専用サービス - N8N連携"""
    
    def __init__(self):
        self.n8n_webhook_url = getattr(Config, 'N8N_WEBHOOK_URL', 'disabled')
        print(f"🔍 DEBUG: EmailSendService初期化")
        print(f"🔍 DEBUG: Config.N8N_WEBHOOK_URL = {Config.N8N_WEBHOOK_URL}")
        print(f"🔍 DEBUG: self.n8n_webhook_url = {self.n8n_webhook_url}")
        self.timeout = 30
        
        # メールアドレスパターン（正規表現）
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # 既知の担当者メールアドレス（デモ用）
        self.staff_emails = {
            "高見": "takami@hbm-web.co.jp",
            "辻川": "tsujikawa@hbm-web.co.jp", 
            "小濱": "kohama@hbm-web.co.jp",
            "部長": "bucho@hbm-web.co.jp",
            "課長": "kacho@hbm-web.co.jp",
            "田中": "katsura@hbm-web.co.jp",
            "田中さん": "katsura@hbm-web.co.jp"
        }
    
    def should_send_email(self, user_message: str, ai_response: str) -> bool:
        """メール送信が必要かどうかを判定"""
        email_keywords = [
            "メール", "送信", "送って", "連絡", "報告", "通知",
            "お知らせ", "共有", "転送", "配信"
        ]
        
        # 田中さんへのメール依頼パターン（柔軟対応）
        tanaka_email_patterns = [
            "田中さんにメール",
            "田中さんに連絡", 
            "田中さんに報告",
            "田中にメール",
            "田中に連絡"
        ]
        
        # パスワード関連キーワード
        password_keywords = [
            "パスワード", "ログイン", "ログインできない",
            "侍", "販売管理ソフト", "システム"
        ]
        
        # 🔥 新機能：フォローアップメール送信パターン
        followup_email_patterns = [
            "もう一度メール送って",
            "再度メール送信",
            "メール再送",
            "もう一回送って",
            "再送して"
        ]
        
        # Web検索結果でメール送信依頼がある場合は特別処理
        if "Web検索結果" in ai_response and any(keyword in user_message for keyword in email_keywords):
            print(f"🔍 DEBUG: Web検索結果 + メール送信キーワード検出")
            return True
        
        # フォローアップメール送信パターンチェック
        has_followup_email = any(pattern in user_message for pattern in followup_email_patterns)
        
        # 田中さんへのメール依頼パターンチェック
        has_tanaka_email = any(pattern in user_message for pattern in tanaka_email_patterns)
        
        # 通常のメール送信キーワードチェック + 田中さん言及
        has_email_keyword = any(keyword in user_message for keyword in email_keywords)
        mentions_tanaka = "田中" in user_message
        
        # パスワード関連のチェック
        has_password_related = any(keyword in user_message for keyword in password_keywords)
        
        # 柔軟な判定ロジック
        result = (
            has_followup_email or  # フォローアップメール送信
            has_tanaka_email or  # 田中さんへのメール依頼
            (has_email_keyword and mentions_tanaka) or  # メール + 田中さん言及
            (has_password_related and mentions_tanaka) or  # パスワード関連 + 田中さん言及
            has_email_keyword  # 🔥 新機能：「メール」キーワードだけでも送信判定 True
        )
        
        print(f"🔍 DEBUG: should_send_email = {result}")
        print(f"🔍 DEBUG: user_message = '{user_message}'")
        print(f"🔍 DEBUG: 検出キーワード = {[kw for kw in email_keywords if kw in user_message]}")
        print(f"🔍 DEBUG: フォローアップメール = {has_followup_email}")
        print(f"🔍 DEBUG: 田中さんメール依頼 = {has_tanaka_email}")
        print(f"🔍 DEBUG: パスワード関連 = {has_password_related}")
        
        return result
    
    def extract_email_request(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """メール送信リクエストの詳細を抽出"""
        email_request = {
            "should_send": False,
            "recipients": [],
            "subject": "",
            "content": ai_response,
            "urgency": "normal",
            "original_request": user_message
        }
        
        if not self.should_send_email(user_message, ai_response):
            return email_request
        
        email_request["should_send"] = True
        
        # 🔥 新機能：柔軟な動的メール生成
        if "田中" in user_message and any(keyword in user_message for keyword in ["侍", "パスワード", "ログイン", "販売管理"]):
            email_request = self._create_dynamic_email(user_message, ai_response)
        # 🔥 新機能：フォローアップメール送信の特別処理
        elif any(pattern in user_message for pattern in ["もう一度メール送って", "再度メール送信", "メール再送", "もう一回送って", "再送して"]):
            email_request = self._create_followup_email(user_message, ai_response)
        # パスワードリセット関連の特別処理
        elif self._is_password_reset_request(user_message):
            email_request = self._create_password_reset_email(user_message, ai_response)
        else:
            # 通常のメール処理
            # 宛先抽出
            recipients = self._extract_recipients(user_message)
            email_request["recipients"] = recipients
            
            # 件名生成
            subject = self._generate_subject(user_message, ai_response)  
            email_request["subject"] = subject
            
            # 緊急度判定
            urgency = self._determine_urgency(user_message)
            email_request["urgency"] = urgency
        
        return email_request
    
    def _extract_recipients(self, message: str) -> List[Dict[str, str]]:
        """メッセージから宛先を抽出"""
        recipients = []
        
        # 1. 直接的なメールアドレス
        email_matches = re.findall(self.email_pattern, message)
        for email in email_matches:
            recipients.append({
                "email": email,
                "name": email.split('@')[0],
                "type": "direct"
            })
        
        # 2. 担当者名からメールアドレス解決
        for name, email in self.staff_emails.items():
            if name in message:
                recipients.append({
                    "email": email,
                    "name": name,
                    "type": "staff"
                })
        
        # 3. 顧客メールアドレス（ドメイン推測）
        customer_patterns = [
            r'(\w+)@(\w+)\.co\.jp',
            r'(\w+)@(\w+)\.com',
            r'(\w+)\.(\w+)@'
        ]
        
        for pattern in customer_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple):
                    email = '@'.join(match) if '@' not in ''.join(match) else ''.join(match)
                    recipients.append({
                        "email": email,
                        "name": "顧客",
                        "type": "customer"
                    })
        
        return recipients
    
    def _detect_context_from_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """AI回答から文脈を検出"""
        context = {
            "mentioned_contacts": [],
            "suggested_action": None,
            "system_context": None
        }
        
        # 田中さんが言及されている場合
        if "田中さん" in ai_response and ("パスワード" in ai_response or "ログイン" in ai_response or "勤怠" in ai_response):
            context["mentioned_contacts"].append({
                "name": "田中さん",
                "email": "katsura@hbm-web.co.jp",
                "reason": "パスワードリセット",
                "confidence": 0.9
            })
            context["suggested_action"] = "password_reset"
            context["system_context"] = "勤怠管理システム"
        
        # 他の担当者言及の検出
        for name in ["高見", "辻川", "小濱"]:
            if f"{name}さん" in ai_response:
                context["mentioned_contacts"].append({
                    "name": f"{name}さん",
                    "email": self.staff_emails.get(name, f"{name.lower()}@hbm-web.co.jp"),
                    "reason": "営業関連",
                    "confidence": 0.7
                })
        
        return context
    
    def _is_password_reset_request(self, message: str) -> bool:
        """パスワードリセット関連のリクエストか判定"""
        password_keywords = ["パスワード", "ログインできない", "ログイン"]
        tanaka_keywords = ["田中", "システムソリューション"]
        
        has_password_issue = any(keyword in message for keyword in password_keywords)
        mentions_tanaka = any(keyword in message for keyword in tanaka_keywords)
        
        return has_password_issue or mentions_tanaka
    
    def _create_dynamic_email(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """ユーザーリクエストに基づいて動的にメール内容を生成"""
        from langchain_openai import ChatOpenAI
        from config import Config
        
        # システム固有のキーワードを検出
        system_keywords = {
            "侍": "販売管理ソフト「侍」",
            "販売管理": "販売管理システム", 
            "勤怠": "勤怠管理システム",
            "有給": "勤怠管理システム",
            "パスワード": "システムパスワード"
        }
        
        detected_system = "業務システム"
        for keyword, system_name in system_keywords.items():
            if keyword in user_message:
                detected_system = system_name
                break
        
        # AIでメール内容を動的生成
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=Config.OPENAI_API_KEY
        )
        
        prompt = f"""
あなたは阪南ビジネスマシンの優秀な事務アシスタントです。
以下のリクエストに基づいて、田中さん宛のビジネスメールを作成してください。

【ユーザーリクエスト】
{user_message}

【AI分析結果】  
{ai_response[:300]}

【検出されたシステム】
{detected_system}

【メール作成指針】
- 田中さんはシステムソリューション課の担当者
- 丁寧で的確なビジネス文書にする
- ユーザーの具体的な要求を正確に伝える
- 必要な情報（システム名、問題内容、緊急度）を含める
- 自然で読みやすい文章にする

【メール形式】
田中様

お世話になっております。

[メイン内容]

【依頼内容】
- システム名: {detected_system}  
- 問題: [具体的な問題]
- 緊急度: [判定]

[依頼文]

どうぞよろしくお願いいたします。

【このメールはAIアシスタントから自動送信されています】
生成時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分')}

メール本文のみを出力してください：
"""
        
        try:
            email_content = llm.invoke(prompt).content
            
            # 件名を動的生成
            if "パスワード" in user_message or "ログイン" in user_message:
                subject = f"【パスワードリセット依頼】{detected_system}"
            elif "問題" in user_message or "エラー" in user_message:
                subject = f"【システム障害報告】{detected_system}"
            elif "質問" in user_message or "問い合わせ" in user_message:
                subject = f"【お問い合わせ】{detected_system}について"
            else:
                subject = f"【ご連絡】{detected_system}について"
            
            return {
                "should_send": True,
                "recipients": [{
                    "email": "katsura@hbm-web.co.jp",
                    "name": "田中さん",
                    "type": "staff"
                }],
                "subject": subject,
                "content": email_content,
                "urgency": "high" if any(kw in user_message for kw in ["緊急", "至急", "すぐ"]) else "normal",
                "original_request": user_message
            }
            
        except Exception as e:
            print(f"❌ AI動的メール生成エラー: {e}")
            # フォールバック: 基本的なメール生成
            return self._create_password_reset_email(user_message, ai_response)

    def _create_dynamic_email(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """ユーザーリクエストに基づいて動的にメール内容を生成"""
        from langchain_openai import ChatOpenAI
        from config import Config
        
        # システム固有のキーワードを検出
        system_keywords = {
            "侍": "販売管理ソフト「侍」",
            "販売管理": "販売管理システム", 
            "勤怠": "勤怠管理システム",
            "有給": "勤怠管理システム",
            "パスワード": "システムパスワード"
        }
        
        detected_system = "業務システム"
        for keyword, system_name in system_keywords.items():
            if keyword in user_message:
                detected_system = system_name
                break
        
        # AIでメール内容を動的生成
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=Config.OPENAI_API_KEY
        )
        
        prompt = f"""
あなたは阪南ビジネスマシンの優秀な事務アシスタントです。
以下のリクエストに基づいて、田中さん宛のビジネスメールを作成してください。

【ユーザーリクエスト】
{user_message}

【AI分析結果】  
{ai_response[:300]}

【検出されたシステム】
{detected_system}

【メール作成指針】
- 田中さんはシステムソリューション課の担当者
- 丁寧で的確なビジネス文書にする
- ユーザーの具体的な要求を正確に伝える
- 必要な情報（システム名、問題内容、緊急度）を含める
- 自然で読みやすい文章にする

【メール形式】
田中様

お世話になっております。

[メイン内容]

【依頼内容】
- システム名: {detected_system}  
- 問題: [具体的な問題]
- 緊急度: [判定]

[依頼文]

どうぞよろしくお願いいたします。

【このメールはAIアシスタントから自動送信されています】
生成時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分')}

メール本文のみを出力してください：
"""
        
        try:
            email_content = llm.invoke(prompt).content
            
            # 件名を動的生成
            if "パスワード" in user_message or "ログイン" in user_message:
                subject = f"【パスワードリセット依頼】{detected_system}"
            elif "問題" in user_message or "エラー" in user_message:
                subject = f"【システム障害報告】{detected_system}"
            elif "質問" in user_message or "問い合わせ" in user_message:
                subject = f"【お問い合わせ】{detected_system}について"
            else:
                subject = f"【ご連絡】{detected_system}について"
            
            return {
                "should_send": True,
                "recipients": [{
                    "email": "katsura@hbm-web.co.jp",
                    "name": "田中さん",
                    "type": "staff"
                }],
                "subject": subject,
                "content": email_content,
                "urgency": "high" if any(kw in user_message for kw in ["緊急", "至急", "すぐ"]) else "normal",
                "original_request": user_message
            }
            
        except Exception as e:
            print(f"❌ AI動的メール生成エラー: {e}")
            # フォールバック: 基本的なメール生成
            return self._create_password_reset_email(user_message, ai_response)

    def _create_followup_email(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """フォローアップメール送信を処理"""
        # 前回と同じメール内容を再送
        return {
            "should_send": True,
            "recipients": [{
                "email": "katsura@hbm-web.co.jp",
                "name": "田中さん",
                "type": "staff"
            }],
            "subject": "【再送】販売管理ソフト「侍」パスワードリセット依頼",
            "content": """田中様

お世話になっております。

先ほど依頼いたしました販売管理ソフト「侍」のパスワードリセットの件について、再度ご連絡させていただきます。

【依頼内容】
- システム名: 販売管理ソフト「侍」
- 問題: パスワードがわからなくなった
- 緊急度: normal

お忙しい中恐れ入りますが、パスワードの再設定をお願いいたします。

どうぞよろしくお願いいたします。

【このメールはAIアシスタントから自動送信されています】
生成時刻: """ + datetime.now().strftime('%Y年%m月%d日 %H時%M分'),
            "urgency": "normal",
            "original_request": user_message
        }

    def _create_password_reset_email(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """パスワードリセット依頼メールを作成"""
        # システムを特定
        system_name = "勤怠管理システム" if "勤怠" in user_message or "有給" in user_message else "業務システム"
        
        # ユーザー名を抽出または推測
        user_name = "LINE AIアシスタント"
        if "私" in user_message:
            user_name = "ご依頼者様"
        
        # AIが生成した追加の文脈情報を活用
        additional_context = ""
        if "勤怠" in ai_response or "有給" in ai_response:
            additional_context = "\n勤怠管理システムでの有給申請に関連する可能性があります。"
        elif "営業" in ai_response:
            additional_context = "\n営業業務関連のシステムアクセスが必要と思われます。"
        
        # より詳細で自然なメール内容を生成
        email_content = f"""田中様

お世話になっております。

{system_name}のパスワードリセットをお願いしたく、ご連絡させていただきました。

【依頼内容】
- システム名: {system_name}
- 依頼者: {user_name}  
- 問題: ログインパスワードが不明
- 緊急度: 高{additional_context}

【状況詳細】
{ai_response[:200]}...

パスワードの再設定をお願いいたします。
お手数をおかけいたしますが、どうぞよろしくお願いいたします。

【このメールはAIアシスタントから自動送信されています】
生成時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分')}"""
        
        return {
            "should_send": True,
            "recipients": [{
                "email": "katsura@hbm-web.co.jp",
                "name": "田中さん",
                "type": "staff"
            }],
            "subject": f"【パスワードリセット依頼】{system_name}",
            "content": email_content,
            "urgency": "high",
            "original_request": user_message
        }
    
    def _generate_subject(self, user_message: str, ai_response: str) -> str:
        """件名を自動生成"""
        
        # キーワード別件名テンプレート
        if "レポート" in user_message:
            if "7月" in user_message:
                return "【阪南ビジネスマシン】7月度営業レポート"
            elif "営業" in user_message:
                return "【阪南ビジネスマシン】営業実績レポート"
            else:
                return "【阪南ビジネスマシン】業務レポート"
        
        elif "トナー" in user_message:
            return "【阪南ビジネスマシン】コピー機トナー交換方法のご案内"
        
        elif "問い合わせ" in user_message or "質問" in user_message:
            return "【阪南ビジネスマシン】お問い合わせへの回答"
        
        elif "売上" in user_message or "実績" in user_message:
            return "【阪南ビジネスマシン】売上実績について"
        
        else:
            # 汎用件名
            today = datetime.now().strftime('%Y年%m月%d日')
            return f"【阪南ビジネスマシン】{today} ご連絡"
    
    def _determine_urgency(self, message: str) -> str:
        """緊急度を判定"""
        urgent_keywords = ["緊急", "至急", "急ぎ", "すぐに", "今すぐ"]
        high_keywords = ["重要", "大事", "優先", "早めに"]
        
        if any(keyword in message for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in message for keyword in high_keywords):
            return "high"
        else:
            return "normal"
    
    def send_email_via_n8n(self, email_request: Dict[str, Any]) -> str:
        """N8N経由でメール送信"""
        
        print(f"🔍 DEBUG: send_email_via_n8n開始")
        print(f"🔍 DEBUG: n8n_webhook_url = {self.n8n_webhook_url}")
        print(f"🔍 DEBUG: URLチェック: not={not self.n8n_webhook_url}, disabled={self.n8n_webhook_url == 'disabled'}, your-n8n={'your-n8n-instance' in self.n8n_webhook_url}")
        
        # N8N無効時の処理（developmentモードでは詳細プレビューを表示）
        if not self.n8n_webhook_url or self.n8n_webhook_url == "disabled" or "your-n8n-instance" in self.n8n_webhook_url:
            print(f"🔍 DEBUG: N8N無効と判定 - プレビューモードに切替")
            return self._format_email_preview(email_request)
        
        # N8N用ペイロード作成（単純構造）
        # 最初の受信者を取得
        first_recipient = email_request["recipients"][0] if email_request["recipients"] else {
            "email": "katsura@hbm-web.co.jp",
            "name": "田中さん"
        }
        
        # 改行コードを統一（N8N対応）
        clean_content = email_request["content"].replace('\\n', '\n').replace('\r\n', '\n')
        
        payload = {
            "recipient_email": first_recipient["email"],
            "recipient_name": first_recipient["name"],
            "email_subject": email_request["subject"],
            "email_content": clean_content,
            "urgency": email_request["urgency"]
        }
        
        print(f"🔍 DEBUG: N8Nに送信するペイロード:")
        print(f"  recipient_email: {payload['recipient_email']}")
        print(f"  recipient_name: {payload['recipient_name']}")
        print(f"  email_subject: {payload['email_subject']}")
        print(f"  urgency: {payload['urgency']}")
        print(f"  email_content: {payload['email_content'][:100]}...")
        
        try:
            print(f"🚀 DEBUG: N8Nにリクエスト送信中...")
            print(f"🚀 DEBUG: URL: {self.n8n_webhook_url}")
            response = requests.post(
                self.n8n_webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            print(f"✅ DEBUG: レスポンス受信 - status_code: {response.status_code}")
            print(f"✅ DEBUG: レスポンステキスト: {response.text}")
            print(f"✅ DEBUG: レスポンスヘッダー: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json() if response.text else {}
                print(f"✅ DEBUG: パース済みレスポンス: {result}")
                message = result.get("message", "メール送信処理を開始しました")
                
                recipients_text = ", ".join([r["name"] for r in email_request["recipients"]])
                return f"""📧 **メール送信完了**

✅ {message}

**宛先**: {recipients_text}
**件名**: {email_request["subject"]}
**緊急度**: {email_request["urgency"]}

メールの配信完了まで少々お時間をいただく場合があります。"""
                
            else:
                return f"⚠️ メール送信処理でエラーが発生しました。(ステータス: {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return "❌ メール送信サーバーに接続できません。N8Nの設定を確認してください。"
        except requests.exceptions.Timeout:
            return "⚠️ メール送信処理がタイムアウトしました。処理は継続されている可能性があります。"
        except requests.exceptions.RequestException as e:
            return f"❌ メール送信中にエラーが発生しました: {str(e)[:100]}..."
    
    def _format_email_preview(self, email_request: Dict[str, Any]) -> str:
        """メール送信プレビュー（N8N無効時）"""
        recipients_text = ", ".join([f"{r['name']} ({r['email']})" for r in email_request["recipients"]])
        
        preview = f"""📧 **メール送信プレビュー**

**宛先**: {recipients_text}
**件名**: {email_request["subject"]}
**緊急度**: {email_request["urgency"]}

**本文**:
{email_request["content"][:200]}...

---
💡 実際のメール送信には N8N ワークフローの設定が必要です。
設定方法については管理者にお問い合わせください。"""
        
        return preview
    
    def process_email_request(self, user_message: str, ai_response: str) -> Tuple[bool, str]:
        """メール送信リクエストを処理する（メイン関数）"""
        
        # メール送信リクエストの抽出
        email_request = self.extract_email_request(user_message, ai_response)
        
        if not email_request["should_send"]:
            return False, ai_response
        
        # 🔥 新機能: AI回答から文脈を検出
        context = self._detect_context_from_ai_response(ai_response)

        # 宛先が見つからない場合の改善された処理
        if not email_request["recipients"]:
            
            # 文脈から推測された連絡先がある場合
            if context["mentioned_contacts"]:
                primary_contact = max(context["mentioned_contacts"], key=lambda x: x["confidence"])
                
                if primary_contact["confidence"] > 0.8:
                    # 高い確信度の場合は自動選択
                    email_request["recipients"] = [{
                        "email": primary_contact["email"],
                        "name": primary_contact["name"],
                        "type": "context_detected"
                    }]
                    
                    # パスワードリセットの特別処理
                    if primary_contact["reason"] == "パスワードリセット":
                        email_request = self._create_password_reset_email(user_message, ai_response)
                        
                    # メール送信実行
                    send_result = self.send_email_via_n8n(email_request)
                    
                    combined_response = f"""{ai_response}

---

📧 **{primary_contact['name']}にメールを送信します**

{send_result}"""
                    
                    return True, combined_response
            
            # 文脈が不明確な場合は従来通りの確認
            additional_message = f"""

メールでお送りしたいのですが、どちらに送りましょうか？
高見さん？辻川さん？それとも他の方でしょうか？"""
            return False, ai_response + additional_message
        
        # N8N経由でメール送信
        send_result = self.send_email_via_n8n(email_request)
        
        # 元の回答 + 送信結果を結合
        combined_response = f"""{ai_response}

---

{send_result}"""
        
        return True, combined_response
    
    def get_staff_email_list(self) -> Dict[str, str]:
        """担当者メールアドレス一覧を取得"""
        return self.staff_emails.copy()
    
    def add_staff_email(self, name: str, email: str) -> bool:
        """担当者メールアドレスを追加"""
        if re.match(self.email_pattern, email):
            self.staff_emails[name] = email
            return True
        return False
    
    def validate_email_format(self, email: str) -> bool:
        """メールアドレス形式の検証"""
        return bool(re.match(self.email_pattern, email))

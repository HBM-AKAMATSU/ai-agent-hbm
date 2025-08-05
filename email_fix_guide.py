#!/usr/bin/env python3
"""
email_send_service.py の修正内容
会話文脈を継承するための具体的な修正コード
"""

def show_exact_modification():
    print("🔧 **email_send_service.py の具体的修正内容**")
    print()
    print("## 📁 **修正ファイル**: `src/services/email_send_service.py`")
    print()
    print("### **1. 新しいメソッドを追加** (140行目付近に追加)")
    
    new_method = '''
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
                "email": "tanaka@hbm-web.co.jp",
                "reason": "パスワードリセット",
                "confidence": 0.9
            })
            context["suggested_action"] = "password_reset"
            context["system_context"] = "勤怠管理システム"
        
        # 他の担当者言及の検出
        for name in ["高見", "辻川", "小濱"]:
            if name in ai_response:
                context["mentioned_contacts"].append({
                    "name": f"{name}さん",
                    "email": f"{name.lower()}@hbm-web.co.jp",
                    "reason": "営業関連",
                    "confidence": 0.7
                })
        
        return context
    '''
    
    print(new_method)
    print()
    print("### **2. process_email_requestメソッドを修正** (240行目付近)")
    print()
    print("**現在のコード** (❌ 問題のある部分):")
    
    current_code = '''
    def process_email_request(self, user_message: str, ai_response: str) -> Tuple[bool, str]:
        # メール送信リクエストの抽出
        email_request = self.extract_email_request(user_message, ai_response)
        
        if not email_request["should_send"]:
            return False, ai_response
        
        # 宛先が見つからない場合の処理
        if not email_request["recipients"]:
            # 簡潔で対話的な案内
            additional_message = f"""

メールでお送りしたいのですが、どちらに送りましょうか？
高見さん？辻川さん？それとも他の方でしょうか？"""
            return False, ai_response + additional_message
    '''
    
    print(current_code)
    print()
    print("**修正後のコード** (✅ 文脈を考慮):")
    
    fixed_code = '''
    def process_email_request(self, user_message: str, ai_response: str) -> Tuple[bool, str]:
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
        
        # 通常の送信処理
        send_result = self.send_email_via_n8n(email_request)
        combined_response = f"""{ai_response}

---

{send_result}"""
        
        return True, combined_response
    '''
    
    print(fixed_code)
    print()
    print("## 🎯 **修正の効果**")
    print()
    print("### **修正前の動作**:")
    print('AI: "田中さんにメールを送信することもできます"')
    print('ユーザー: "メールを送っていただけますか？"')
    print('AI: "高見さん？辻川さん？それとも他の方でしょうか？"')
    print()
    print("### **修正後の動作**:")
    print('AI: "田中さんにメールを送信することもできます"')
    print('ユーザー: "メールを送っていただけますか？"')
    print('AI: "田中さんにメールを送信します" + パスワードリセットメール送信')
    print()
    print("## 🔧 **修正手順**")
    print("1. `src/services/email_send_service.py` を開く")
    print("2. 140行目付近に `_detect_context_from_ai_response` メソッドを追加")
    print("3. 240行目付近の `process_email_request` メソッドを上記のコードに置き換え")
    print("4. サーバーを再起動")

if __name__ == "__main__":
    show_exact_modification()

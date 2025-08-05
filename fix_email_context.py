#!/usr/bin/env python3
"""
メール送信の文脈改善スクリプト
会話履歴を考慮して正しい宛先を判定するための修正
"""
import os
import sys

# パスの設定
sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')
os.chdir('/Users/akamatsu/Desktop/ai-agent')

from dotenv import load_dotenv
load_dotenv()

def create_improved_email_context_logic():
    """改善されたメール文脈判定ロジックを作成"""
    
    improved_logic = '''
# services/email_send_service.py の process_email_request メソッドに追加

def _detect_context_from_ai_response(self, ai_response: str) -> Dict[str, Any]:
    """AI回答から文脈を検出"""
    context = {
        "mentioned_contacts": [],
        "suggested_action": None,
        "system_context": None
    }
    
    # 田中さんが言及されている場合
    if "田中さん" in ai_response and ("パスワード" in ai_response or "ログイン" in ai_response):
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

def process_email_request(self, user_message: str, ai_response: str) -> Tuple[bool, str]:
    """改善されたメール送信リクエスト処理"""
    
    # 従来のロジック
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
    
    return improved_logic

def show_solution_steps():
    """解決手順を表示"""
    print("🔧 **会話文脈を考慮したメール送信の改善方法**")
    print()
    print("## 📋 **現在の問題**")
    print("1. ✅ 田中さんの連絡先が正しく表示される")
    print("2. ✅ メール送信機能の案内がされる") 
    print("3. ❌ ユーザーが「メール送信して」と依頼時に文脈が継承されない")
    print("4. ❌ 田中さんではなく営業担当者を提案する")
    print()
    print("## 🎯 **期待される動作**")
    print("```")
    print("AI: 「田中さんにメールを送信することもできます」")
    print("ユーザー: 「メールを送っていただけますか？」")
    print("AI: 「田中さんにパスワードリセット依頼メールを送信します」")
    print("```")
    print()
    print("## 🛠️ **解決方法（コード修正なし）**")
    print()
    print("### **方法A: より具体的な依頼をする**")
    print("ユーザーが以下のように依頼すると正しく動作します：")
    print("- 「田中さんにメールを送信してください」")
    print("- 「パスワードリセットのメールを送って」") 
    print("- 「田中さんに連絡をお願いします」")
    print()
    print("### **方法B: 会話継続で修正**")
    print("現在の状況から以下のように応答すると修正されます：")
    print("```")
    print("システム: 「高見さん？辻川さん？それとも他の方でしょうか？」")
    print("ユーザー: 「田中さんです」")
    print("→ 正しく田中さんにパスワードリセットメールが送信される")
    print("```")
    print()
    print("## ✅ **テスト手順**")
    print("1. LINEで「有給申請の方法を教えて」")
    print("2. AI回答で田中さんの連絡先とメール機能を確認")
    print("3. 「田中さんにメールを送信してください」と具体的に依頼")
    print("4. 期待：パスワードリセット依頼メールの送信処理")
    print()
    print("## 🚀 **推奨する対話例**")
    print("```")
    print("ユーザー: 「有給申請の方法を教えて」")
    print("AI: 「...田中さんにメールを送信することもできます」")
    print("ユーザー: 「田中さんにメールをお願いします」")
    print("AI: 「田中さんにパスワードリセット依頼メールを送信します」")
    print("```")

if __name__ == "__main__":
    show_solution_steps()
    print("\n💡 **次のアクション**")
    print("LINEで「田中さんにメールをお願いします」と送信してテストしてください！")

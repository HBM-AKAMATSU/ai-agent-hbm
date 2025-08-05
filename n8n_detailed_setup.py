#!/usr/bin/env python3
"""
N8N ワークフロー設定ガイド
阪南ビジネスマシン メール送信機能の有効化
"""

def show_n8n_setup_steps():
    """N8N設定の詳細手順"""
    
    print("🔧 **N8N ワークフロー設定ガイド**")
    print()
    print("## 📋 **前提条件**")
    print("1. N8Nがインストール済み（http://localhost:5678 でアクセス可能）")
    print("2. Gmailアカウント（送信用）")
    print("3. 管理者権限")
    print()
    
    print("## 🚀 **Step 1: N8N起動確認**")
    print()
    print("```bash")
    print("# Dockerの場合")
    print("docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n")
    print()
    print("# npmの場合")
    print("npx n8n")
    print("```")
    print()
    print("ブラウザで http://localhost:5678 にアクセスし、N8Nのダッシュボードが表示されることを確認")
    print()
    
    print("## 📧 **Step 2: Gmail認証設定**")
    print()
    print("### **2-1. Gmailクレデンシャルの作成**")
    print("1. N8Nダッシュボードで「Settings」→「Credentials」をクリック")
    print("2. 「Add Credential」をクリック")
    print("3. 「Gmail OAuth2 API」を選択")
    print()
    print("### **2-2. Google Cloud Consoleでの設定**")
    print("1. https://console.cloud.google.com/ にアクセス")
    print("2. 新しいプロジェクトを作成またはプロジェクトを選択")
    print("3. 「APIs & Services」→「Library」で「Gmail API」を有効化")
    print("4. 「APIs & Services」→「Credentials」でOAuth 2.0クライアントIDを作成")
    print("5. 承認済みリダイレクトURIに以下を追加：")
    print("   `http://localhost:5678/rest/oauth2-credential/callback`")
    print()
    print("### **2-3. N8Nでの認証完了**")
    print("1. Google CloudのClient IDとClient Secretを入力")
    print("2. 「Connect my account」をクリックしてGoogleアカウントで認証")
    print("3. 認証が成功したら「Save」をクリック")
    print()
    
    print("## 🔗 **Step 3: ワークフロー作成**")
    print()
    print("### **3-1. 新しいワークフロー作成**")
    print("1. N8Nダッシュボードで「+ New Workflow」をクリック")
    print("2. ワークフロー名を「阪南ビジネスマシン メール送信」に設定")
    print()
    print("### **3-2. ノードの追加**")
    print()
    print("**A. Webhookノード（トリガー）**")
    print("1. 「+」→「Trigger」→「Webhook」を追加")
    print("2. 設定：")
    print("   - HTTP Method: POST")
    print("   - Path: hannan-email-webhook")
    print("   - Response Mode: 'Using Respond to Webhook' Node")
    print()
    print("**B. Setノード（データ変換）**")
    print("1. Webhookノードの右に「+」→「Data」→「Set」を追加")
    print("2. 以下の値を設定：")
    
    assignments = [
        ("recipient_email", "{{ $json.email_data.recipients[0].email }}"),
        ("recipient_name", "{{ $json.email_data.recipients[0].name }}"),
        ("email_subject", "{{ $json.email_data.subject }}"),
        ("email_content", "{{ $json.email_data.content }}"),
        ("urgency", "{{ $json.email_data.urgency }}")
    ]
    
    for name, value in assignments:
        print(f"   - Name: {name}")
        print(f"     Value: {value}")
    print()
    
    print("**C. Gmailノード（メール送信）**")
    print("1. Setノードの右に「+」→「Regular」→「Gmail」を追加")
    print("2. Operation: Send Email")
    print("3. 設定：")
    print("   - To Email: {{ $json.recipient_email }}")
    print("   - Subject: {{ $json.email_subject }}")
    print("   - Email Type: Text")
    print("   - Message: {{ $json.email_content }}")
    print("   - Credentials: 作成したGmail OAuth2クレデンシャルを選択")
    print()
    
    print("**D. Respond to Webhookノード（レスポンス）**")
    print("1. Gmailノードの右に「+」→「Flow」→「Respond to Webhook」を追加")
    print("2. 設定：")
    print("   - Status Code: 200")
    print("   - Response Body: JSON")
    print("   - Body内容：")
    print("     ```json")
    print("     {")
    print('       "status": "success",')
    print('       "message": "メールを正常に送信しました",')
    print('       "timestamp": "{{ $now.toISO() }}"')
    print("     }")
    print("     ```")
    print()
    
    print("### **3-3. ワークフロー保存と有効化**")
    print("1. 右上の「Save」をクリック")
    print("2. 右上のトグルスイッチで「Active」に変更")
    print("3. Webhookノードをクリックして「Copy」からWebhook URLをコピー")
    print()
    
    print("## 🌐 **Step 4: Webhook URL の取得**")
    print()
    print("1. Webhookノードをクリック")
    print("2. 「Test URL」または「Production URL」をコピー")
    print("3. 形式: `http://localhost:5678/webhook/hannan-email-webhook`")
    print()
    
    print("## ⚙️ **Step 5: 環境変数設定**")
    print()
    print("### **5-1. .envファイルの更新**")
    print("```bash")
    print("# .env ファイルに以下を追加")
    print("N8N_WEBHOOK_URL=http://localhost:5678/webhook/hannan-email-webhook")
    print("```")
    print()
    print("### **5-2. config.py の確認**")
    print("```python")
    print("# config.py で正しく読み込まれているか確認")
    print("N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')")
    print("```")
    print()
    
    print("## 🧪 **Step 6: テスト実行**")
    print()
    print("### **6-1. N8Nでのテスト**")
    print("1. Webhookノードの「Listen for calls」をクリック")
    print("2. 以下のテストデータをPOST送信：")
    
    test_payload = """{
  "action": "send_email",
  "email_data": {
    "recipients": [
      {
        "email": "test@example.com",
        "name": "テストユーザー"
      }
    ],
    "subject": "【テスト】N8N連携確認",
    "content": "N8Nワークフローのテストメールです。",
    "urgency": "normal"
  }
}"""
    
    print("```json")
    print(test_payload)
    print("```")
    print()
    
    print("### **6-2. AIアシスタントでのテスト**")
    print("1. アプリケーションを再起動")
    print("2. LINEで「田中さんにメールをお願いします」と送信")
    print("3. 「メール送信完了」メッセージが表示されることを確認")
    print()
    
    print("## 🔧 **トラブルシューティング**")
    print()
    print("### **よくある問題と解決方法**")
    print()
    print("**1. 「N8N連携は現在無効です」が表示される**")
    print("- .envファイルのN8N_WEBHOOK_URLが正しく設定されているか確認")
    print("- アプリケーションを再起動")
    print()
    print("**2. Gmail認証エラー**")
    print("- Google Cloud ConsoleでGmail APIが有効化されているか確認")
    print("- OAuth 2.0のリダイレクトURIが正しく設定されているか確認")
    print("- Gmailアカウントで2段階認証が有効になっているか確認")
    print()
    print("**3. Webhook呼び出しエラー**")
    print("- N8Nワークフローがアクティブになっているか確認")
    print("- Webhook URLが正しくコピーされているか確認")
    print("- ファイアウォールやプロキシの設定を確認")
    print()
    
    print("## 🚀 **本番環境設定（追加設定）**")
    print()
    print("### **外部アクセス用設定**")
    print("```bash")
    print("# Docker Composeでの本番環境設定")
    print("N8N_HOST=your-domain.com")
    print("N8N_PORT=5678") 
    print("N8N_PROTOCOL=https")
    print("WEBHOOK_URL=https://your-domain.com/")
    print("```")
    print()
    print("### **セキュリティ設定**")
    print("```bash")
    print("N8N_BASIC_AUTH_ACTIVE=true")
    print("N8N_BASIC_AUTH_USER=admin")
    print("N8N_BASIC_AUTH_PASSWORD=secure-password")
    print("```")

def show_test_commands():
    """テスト用コマンド"""
    print()
    print("## 🧪 **テスト用cURLコマンド**")
    print()
    print("```bash")
    print("# Webhook直接テスト")
    print("curl -X POST http://localhost:5678/webhook/hannan-email-webhook \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{")
    print('    "action": "send_email",')
    print('    "email_data": {')
    print('      "recipients": [{"email": "test@example.com", "name": "テスト"}],')
    print('      "subject": "テストメール",')
    print('      "content": "N8Nテストです",')
    print('      "urgency": "normal"')
    print('    }')
    print('  }'")
    print("```")

if __name__ == "__main__":
    show_n8n_setup_steps()
    show_test_commands()

#!/usr/bin/env python3
"""
N8N ワークフロー作成ガイド（初心者向け）
既存のN8N環境でメール送信ワークフローを作成
"""

def show_browser_setup_guide():
    """ブラウザでの詳細設定手順"""
    
    print("🌐 **N8N ワークフロー作成ガイド（初心者向け）**")
    print("=" * 60)
    print()
    
    print("## 🚀 **Step 1: N8Nダッシュボードにアクセス**")
    print()
    print("1. ブラウザで https://n8n.xvps.jp/ を開く")
    print("2. ログイン画面が表示されたら、管理者から教えてもらったIDとパスワードでログイン")
    print("3. ダッシュボード（メイン画面）が表示されることを確認")
    print()
    print("   🖥️ ダッシュボードには以下が表示されます：")
    print("   • 左側：メニュー（Workflows, Credentials, など）")
    print("   • 中央：ワークフロー一覧")
    print("   • 右上：+ New Workflow ボタン")
    print()
    
    print("## 📝 **Step 2: 新しいワークフローを作成**")
    print()
    print("1. 右上の「+ New Workflow」ボタンをクリック")
    print("2. ワークフロー編集画面が開きます")
    print()
    print("   🖥️ 編集画面の構成：")
    print("   • 左側：ノード一覧（検索可能）")
    print("   • 中央：ワークフローキャンバス（ここにノードを配置）")
    print("   • 右側：選択したノードの設定画面")
    print("   • 上部：保存、実行、アクティブ化ボタン")
    print()
    
    print("## 📧 **Step 3: メール送信ワークフローの作成**")
    print()
    print("### **3-1. Webhookノード（受信トリガー）の追加**")
    print()
    print("1. 左側の検索ボックスに「webhook」と入力")
    print("2. 「Webhook」ノードをクリック")
    print("3. 中央のキャンバスにノードが追加されます")
    print("4. Webhookノードをクリックして設定を開く")
    print()
    print("   ⚙️ **Webhookノードの設定：**")
    print("   • HTTP Method: POST を選択")
    print("   • Path: hannan-email-webhook と入力")
    print("   • Response Mode: 'Using Respond to Webhook' Node を選択")
    print("   • 設定完了後、右上の「Done」をクリック")
    print()
    
    print("### **3-2. Setノード（データ変換）の追加**")
    print()
    print("1. Webhookノードの右側の小さな「+」をクリック")
    print("2. 検索ボックスに「set」と入力")
    print("3. 「Set」ノードをクリック")
    print("4. Setノードをクリックして設定を開く")
    print()
    print("   ⚙️ **Setノードの設定：**")
    print("   以下の5つの値を設定します（「Add Value」で追加）：")
    print()
    print("   **1つ目：**")
    print("   • Name: recipient_email")
    print("   • Value: {{ $json.email_data.recipients[0].email }}")
    print()
    print("   **2つ目：**")
    print("   • Name: recipient_name")
    print("   • Value: {{ $json.email_data.recipients[0].name }}")
    print()
    print("   **3つ目：**")
    print("   • Name: email_subject")
    print("   • Value: {{ $json.email_data.subject }}")
    print()
    print("   **4つ目：**")
    print("   • Name: email_content")
    print("   • Value: {{ $json.email_data.content }}")
    print()
    print("   **5つ目：**")
    print("   • Name: urgency")
    print("   • Value: {{ $json.email_data.urgency }}")
    print()
    print("   • 全て入力したら「Done」をクリック")
    print()
    
    print("### **3-3. Gmailノード（メール送信）の追加**")
    print()
    print("1. Setノードの右側の「+」をクリック")
    print("2. 検索ボックスに「gmail」と入力")
    print("3. 「Gmail」ノードをクリック")
    print("4. Gmailノードをクリックして設定を開く")
    print()
    print("   ⚙️ **Gmailノードの設定：**")
    print("   • Operation: Send Email を選択")
    print("   • To Email: {{ $json.recipient_email }}")
    print("   • Subject: {{ $json.email_subject }}")
    print("   • Email Type: Text を選択")
    print("   • Message: {{ $json.email_content }}")
    print()
    print("   🔐 **Gmail認証（重要）：**")
    print("   • Credential: 「Create New Credential」をクリック")
    print("   • 「Gmail OAuth2 API」を選択")
    print("   • Google Cloud Consoleでの設定が必要（後で詳しく説明）")
    print()
    
    print("### **3-4. Respond to Webhookノード（レスポンス）の追加**")
    print()
    print("1. Gmailノードの右側の「+」をクリック")
    print("2. 検索ボックスに「respond」と入力")
    print("3. 「Respond to Webhook」ノードをクリック")
    print("4. ノードをクリックして設定を開く")
    print()
    print("   ⚙️ **Respond to Webhookノードの設定：**")
    print("   • Status Code: 200")
    print("   • Response Body Type: JSON を選択")
    print("   • JSON内容：")
    
    response_json = """{
  "status": "success",
  "message": "メールを正常に送信しました",
  "timestamp": "{{ $now.toISO() }}"
}"""
    
    print("   ```json")
    print(response_json)
    print("   ```")
    print("   • 設定完了後「Done」をクリック")
    print()

def show_gmail_auth_guide():
    """Gmail認証設定の詳細ガイド"""
    
    print("## 🔐 **Gmail認証設定（重要）**")
    print("=" * 40)
    print()
    
    print("### **Gmail認証が必要な理由**")
    print("N8NからGmailでメールを送信するために、Googleアカウントの認証が必要です。")
    print()
    
    print("### **事前準備**")
    print("1. Gmailアカウント（送信に使用するアカウント）")
    print("2. Google Cloud Console へのアクセス権限")
    print()
    
    print("### **Google Cloud Console での設定**")
    print()
    print("**Step A: プロジェクト作成・選択**")
    print("1. https://console.cloud.google.com/ にアクセス")
    print("2. 既存プロジェクトを選択、または新しいプロジェクトを作成")
    print()
    
    print("**Step B: Gmail API有効化**")
    print("1. 左メニューから「APIs & Services」→「Library」をクリック")
    print("2. 検索ボックスに「Gmail API」と入力")
    print("3. 「Gmail API」をクリック")
    print("4. 「有効にする」ボタンをクリック")
    print()
    
    print("**Step C: OAuth 2.0認証情報作成**")
    print("1. 左メニューから「APIs & Services」→「Credentials」をクリック")
    print("2. 「+ 認証情報を作成」→「OAuth クライアント ID」をクリック")
    print("3. アプリケーションの種類：「ウェブ アプリケーション」を選択")
    print("4. 名前：「N8N Gmail Integration」など任意の名前を入力")
    print("5. 承認済みのリダイレクト URI に以下を追加：")
    print("   `https://n8n.xvps.jp/rest/oauth2-credential/callback`")
    print("6. 「作成」をクリック")
    print("7. 表示されたクライアントIDとクライアントシークレットをメモ")
    print()
    
    print("### **N8Nでの認証設定**")
    print()
    print("1. N8NのGmailノード設定で「Create New Credential」をクリック")
    print("2. 「Gmail OAuth2 API」を選択")
    print("3. Google Cloud ConsoleでメモしたClient IDとClient Secretを入力")
    print("4. 「Connect my account」をクリック")
    print("5. Googleの認証画面でログインし、アクセスを許可")
    print("6. 認証成功後「Save」をクリック")
    print()

def show_final_steps():
    """最終設定とテスト"""
    
    print("## 🎯 **最終設定とテスト**")
    print("=" * 30)
    print()
    
    print("### **ワークフローの保存と有効化**")
    print()
    print("1. 画面右上の「Save」ボタンをクリック")
    print("2. ワークフロー名を入力：「阪南ビジネスマシン メール送信」")
    print("3. 「Save」で保存完了")
    print("4. 画面右上のトグルスイッチをクリックして「Active」に変更")
    print("   （グレー → 緑色に変わればOK）")
    print()
    
    print("### **Webhook URLの取得**")
    print()
    print("1. Webhookノードをクリック")
    print("2. 「Copy」ボタンをクリックしてURLをコピー")
    print("3. URLは以下のような形式になります：")
    print("   `https://n8n.xvps.jp/webhook/hannan-email-webhook`")
    print()
    
    print("### **環境変数の設定**")
    print()
    print("コピーしたWebhook URLを阪南ビジネスマシンのシステムに設定：")
    print()
    print("```bash")
    print("# .envファイルに追加")
    print("N8N_WEBHOOK_URL=https://n8n.xvps.jp/webhook/hannan-email-webhook")
    print("```")
    print()
    
    print("### **アプリケーション再起動**")
    print()
    print("```bash")
    print("cd /Users/akamatsu/Desktop/ai-agent/src")
    print("# Ctrl+C で停止")
    print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    print("```")
    print()
    
    print("### **動作テスト**")
    print()
    print("1. **N8Nでのテスト**：")
    print("   • Webhookノードの「Listen for calls」をクリック")
    print("   • 別タブでテストデータを送信（cURLコマンド）")
    print()
    print("2. **LINEでのテスト**：")
    print("   • 「有給申請の方法を教えて」")
    print("   • 「田中さんにメールをお願いします」")
    print()
    print("3. **期待される結果**：")
    print("   • ❌ ~~「N8N連携は現在無効です」~~")
    print("   • ✅ **「メール送信完了」**")

def create_test_data():
    """テスト用データ"""
    
    print("\n## 🧪 **テスト用データ**")
    print("=" * 20)
    print()
    
    test_curl = """curl -X POST https://n8n.xvps.jp/webhook/hannan-email-webhook \\
  -H "Content-Type: application/json" \\
  -d '{
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
  }'"""
    
    print("**cURLコマンドでのテスト：**")
    print("```bash")
    print(test_curl)
    print("```")

if __name__ == "__main__":
    show_browser_setup_guide()
    show_gmail_auth_guide()
    show_final_steps()
    create_test_data()

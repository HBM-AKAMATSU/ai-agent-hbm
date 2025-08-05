#!/bin/bash
# quick_n8n_setup.sh
# N8N簡単セットアップスクリプト

echo "🚀 N8N 簡単セットアップ"
echo ""

# Step 1: N8N起動
echo "## Step 1: N8N起動"
echo "Dockerでn8nを起動します..."
echo ""

# N8Nコンテナが既に動いているかチェック
if docker ps | grep -q "n8n"; then
    echo "✅ N8Nは既に起動しています"
else
    echo "🔄 N8Nを起動中..."
    docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
    
    if [ $? -eq 0 ]; then
        echo "✅ N8N起動完了"
        echo "   URL: http://localhost:5678"
    else
        echo "❌ N8N起動失敗"
        echo "   npmでの起動を試してください: npx n8n"
        exit 1
    fi
fi

echo ""

# Step 2: 接続確認
echo "## Step 2: 接続確認"
echo "N8Nへの接続を確認中..."

sleep 5  # N8N起動待ち

if curl -s http://localhost:5678 > /dev/null; then
    echo "✅ N8Nに正常に接続できました"
    echo "   ブラウザで http://localhost:5678 を開いてください"
else
    echo "❌ N8Nに接続できません"
    echo "   しばらく待ってから再度確認してください"
fi

echo ""

# Step 3: 設定ファイル更新
echo "## Step 3: 環境変数設定"
echo ""

ENV_FILE=".env"
WEBHOOK_URL="N8N_WEBHOOK_URL=http://localhost:5678/webhook/hannan-email-webhook"

if [ -f "$ENV_FILE" ]; then
    if grep -q "N8N_WEBHOOK_URL" "$ENV_FILE"; then
        echo "⚠️ N8N_WEBHOOK_URLは既に設定されています"
        echo "   現在の設定:"
        grep "N8N_WEBHOOK_URL" "$ENV_FILE"
    else
        echo "$WEBHOOK_URL" >> "$ENV_FILE"
        echo "✅ .envファイルにN8N_WEBHOOK_URLを追加しました"
    fi
else
    echo "$WEBHOOK_URL" > "$ENV_FILE"
    echo "✅ .envファイルを作成し、N8N_WEBHOOK_URLを設定しました"
fi

echo ""

# Step 4: 次のステップガイド
echo "## 🎯 次のステップ"
echo ""
echo "1. ブラウザで http://localhost:5678 を開く"
echo "2. N8Nアカウントを作成/ログイン"
echo "3. 以下のワークフローを作成："
echo ""
echo "   📧 **メール送信ワークフロー**"
echo "   • Webhook (POST: hannan-email-webhook)"
echo "   • Set (データ変換)"
echo "   • Gmail (メール送信)"
echo "   • Respond to Webhook (レスポンス)"
echo ""
echo "4. Gmail OAuth2認証を設定"
echo "5. ワークフローをアクティブ化"
echo "6. アプリケーションを再起動"
echo ""

# Step 5: テストコマンド提供
echo "## 🧪 テストコマンド"
echo ""
echo "設定完了後、以下でテストできます："
echo ""
echo "curl -X POST http://localhost:5678/webhook/hannan-email-webhook \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"action\": \"send_email\","
echo "    \"email_data\": {"
echo "      \"recipients\": [{\"email\": \"test@example.com\", \"name\": \"テスト\"}],"
echo "      \"subject\": \"テストメール\","
echo "      \"content\": \"N8N設定テストです\","
echo "      \"urgency\": \"normal\""
echo "    }"
echo "  }'"
echo ""

echo "## 📚 詳細なガイド"
echo ""
echo "詳細な設定方法は以下のファイルを参照："
echo "• n8n_detailed_setup.py"
echo "• check_n8n_setup.py" 
echo ""

echo "🎉 **簡単セットアップ完了！**"
echo "詳細設定のため、N8Nダッシュボードでワークフローを作成してください。"

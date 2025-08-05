# N8N Gmail メール送信ワークフロー設定ガイド

## 🚀 N8N初期セットアップ

### 1. N8Nインストール
```bash
# NPM経由でインストール
npm install n8n -g

# または Docker経由
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

### 2. N8N起動・アクセス
```bash
# ローカル起動
n8n start

# ブラウザでアクセス
# http://localhost:5678
```

### 3. Googleアカウント認証設定
```
1. N8N管理画面 → Settings → Credentials
2. "Add Credentials" → "Gmail OAuth2 API"
3. Google Cloud Console設定:
   - APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client IDs
   - Application type: Web application
   - Authorized redirect URIs: http://localhost:5678/rest/oauth2-credential/callback
4. Client ID・Client Secret を N8N に設定
5. "Connect my account" でGoogle認証完了
```

## 📧 メール送信ワークフロー作成

### ワークフロー構成
```
Webhook → Code → Gmail → Respond to Webhook
   ↓        ↓      ↓           ↓
受信    データ処理  メール送信  応答返却
```

### Step 1: Webhook ノード設定
```json
{
  "name": "Webhook - Email Request",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "hannan-email-send",
    "responseMode": "responseNode"
  }
}
```

### Step 2: Code ノード設定（データ処理）
```javascript
// N8N Code ノード内のJavaScript
const webhookData = $input.first().json;

// 受信データの解析
let emailData = {};
if (webhookData.email_data) {
  emailData = webhookData.email_data;
} else {
  // フォールバック：直接データがある場合
  emailData = webhookData;
}

// 宛先リスト処理
let toAddresses = [];
if (emailData.recipients && Array.isArray(emailData.recipients)) {
  toAddresses = emailData.recipients.map(recipient => recipient.email).join(', ');
} else if (emailData.recipients) {
  toAddresses = emailData.recipients;
} else {
  toAddresses = 'your-default-email@gmail.com';
}

// 件名処理
let subject = emailData.subject || '【阪南ビジネスマシン】ご連絡';

// 本文処理
let content = emailData.content || 'お疲れさまです。';

// 緊急度による件名調整
if (emailData.urgency === 'urgent') {
  subject = '【緊急】' + subject;
} else if (emailData.urgency === 'high') {
  subject = '【重要】' + subject;
}

// HTML形式メール本文作成
const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .header { background-color: #f4f4f4; padding: 20px; text-align: center; }
    .content { padding: 20px; }
    .footer { background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; }
    .signature { margin-top: 30px; border-top: 1px solid #ccc; padding-top: 15px; }
  </style>
</head>
<body>
  <div class="header">
    <h2>阪南ビジネスマシン株式会社</h2>
  </div>
  <div class="content">
    <p>お疲れさまです。</p>
    <div style="white-space: pre-wrap;">${content}</div>
    <div class="signature">
      <p>---<br>
      阪南ビジネスマシン株式会社<br>
      官需課<br>
      営業支援AI システム<br>
      https://hbm-web.co.jp/</p>
    </div>
  </div>
  <div class="footer">
    <p>このメールは営業支援AIシステムより自動送信されました。</p>
  </div>
</body>
</html>
`;

// 送信用データを返す
return [{
  json: {
    to: toAddresses,
    subject: subject,
    html: htmlContent,
    text: content,
    original_request: emailData.original_request || '',
    urgency: emailData.urgency || 'normal'
  }
}];
```

### Step 3: Gmail ノード設定
```json
{
  "name": "Gmail - Send Email",
  "type": "n8n-nodes-base.gmail",
  "parameters": {
    "resource": "message",
    "operation": "send",
    "to": "={{ $json.to }}",
    "subject": "={{ $json.subject }}",
    "emailFormat": "html",
    "htmlBody": "={{ $json.html }}"
  }
}
```

### Step 4: Respond to Webhook ノード設定
```json
{
  "name": "Respond Success",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "responseCode": 200,
    "responseBody": "={{ JSON.stringify({ 'status': 'success', 'message': 'メール送信完了', 'to': $('Gmail - Send Email').item.json.to, 'timestamp': new Date().toISOString() }) }}"
  }
}
```

### Step 5: エラーハンドリング追加
```javascript
// Error ノード設定
{
  "name": "Error Response",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "responseCode": 500,
    "responseBody": "{{ JSON.stringify({ 'status': 'error', 'message': 'メール送信エラー', 'error': $node['Gmail - Send Email'].json.error }) }}"
  }
}
```

## 🔧 環境変数設定

### .env ファイル更新
```bash
# N8N Webhook URL を実際の値に更新
N8N_WEBHOOK_URL=http://localhost:5678/webhook/hannan-email-send

# または本番環境
# N8N_WEBHOOK_URL=https://your-n8n-domain.com/webhook/hannan-email-send
```

## 🧪 テスト手順

### 1. N8Nワークフロー動作確認
```bash
# curlでテスト
curl -X POST http://localhost:5678/webhook/hannan-email-send \
  -H "Content-Type: application/json" \
  -d '{
    "action": "send_email",
    "email_data": {
      "recipients": [{"email": "test@example.com", "name": "テスト"}],
      "subject": "テストメール",
      "content": "これはテストメールです。",
      "urgency": "normal"
    }
  }'
```

### 2. AIシステム経由テスト
```
LINEメッセージ: "高見さんの7月レポートを高見さんにメールで送って"
期待動作:
1. 高見さんの7月レポート生成
2. メール送信依頼認識
3. N8N経由でGmail送信
4. 送信完了通知
```

## 🔐 セキュリティ設定

### Gmail App Password設定
```
1. Googleアカウント → セキュリティ
2. 2段階認証 を有効化
3. アプリパスワード → メール → デバイス選択
4. 生成されたパスワードをN8Nに設定
```

### IP制限・認証設定
```javascript
// Webhook認証追加（オプション）
if (!$json.source || $json.source !== 'hannan_business_machine_ai') {
  throw new Error('不正なリクエストです');
}
```

## 📊 監視・ログ設定

### ログ記録ノード追加
```javascript
// Log ノード
console.log('メール送信実行:', {
  timestamp: new Date().toISOString(),
  to: $json.to,
  subject: $json.subject,
  urgency: $json.urgency
});
```

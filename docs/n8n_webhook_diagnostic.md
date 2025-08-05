# n8n_webhook_diagnostic.md - n8nメール送信問題の診断と修復ガイド

## 🔍 問題の診断結果

### 現状
- ✅ n8nサーバー稼働中 (https://n8n.xvps.jp)
- ❌ Webhookエンドポイント404エラー
  - `https://n8n.xvps.jp/webhook/hannan-email-webhook`
  - `https://n8n.xvps.jp/webhook-test/hannan-email-webhook`

### 原因
1. **Webhookワークフローが削除または無効化されている**
2. **エンドポイントのパスが変更されている**
3. **n8nワークフローの設定ミス**

## 🛠️ 修復手順

### ステップ1: n8nにログインしてワークフロー確認

1. https://n8n.xvps.jp にアクセス
2. ログイン後、ワークフロー一覧を確認
3. 「hannan-email-webhook」または類似のメール送信ワークフローを探す

### ステップ2: 新しいメール送信ワークフローを作成

以下のワークフロー構成を推奨：

```json
{
  "name": "Hannan Email Webhook",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook",
      "parameters": {
        "path": "hannan-email-webhook",
        "httpMethod": "POST"
      }
    },
    {
      "type": "n8n-nodes-base.gmail",
      "name": "Gmail",
      "parameters": {
        "operation": "send",
        "to": "={{ $json.recipient_email }}",
        "subject": "={{ $json.email_subject }}",
        "message": "={{ $json.email_content }}"
      }
    }
  ]
}
```

### ステップ3: 代替案 - 新しいエンドポイントURL作成

新しいWebhookワークフローを作成し、エンドポイントURLを取得して.envファイルを更新：

```bash
# .envファイルの更新例
N8N_WEBHOOK_URL=https://n8n.xvps.jp/webhook/new-hannan-email-webhook
```

## 🔧 一時的な回避策

メール送信を復旧するまでの間、以下のいずれかの方法を選択：

### 案1: メール送信を無効化
```python
# .envファイルでWebhook URLを無効化
N8N_WEBHOOK_URL=disabled
```

### 案2: ローカルテスト用のモックサーバー
```python
# config.pyに一時的な設定追加
N8N_WEBHOOK_URL = "http://localhost:3000/webhook/test"  # テスト用
```

## 📧 テスト手順

新しいWebhookエンドポイントが設定できたら、以下でテスト：

```bash
curl -X POST https://n8n.xvps.jp/webhook/新しいエンドポイント \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "katsura@hbm-web.co.jp",
    "recipient_name": "田中さん",
    "email_subject": "【テスト】メール送信復旧テスト",
    "email_content": "n8nメール送信機能のテストです。",
    "urgency": "normal"
  }'
```

## 🚀 完全復旧後の確認

1. ✅ n8nワークフローが正常動作
2. ✅ メール送信テストが成功
3. ✅ AIエージェントからのメール送信が機能
4. ✅ 「田中さんにメールお願いします」で正常送信

---

**次のアクション**: 
1. n8nダッシュボードでワークフロー状態を確認
2. 必要に応じて新しいWebhookワークフローを作成
3. 新しいエンドポイントURLで.envファイルを更新
4. テスト実行

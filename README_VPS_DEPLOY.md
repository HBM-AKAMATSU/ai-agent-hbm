# 🚀 VPS安全デプロイ - 実行ガイド

n8n.xvps.jp (210.131.210.25) での既存サービスと**絶対に競合しない**安全なデプロイ手順

## 📋 事前準備（必須）

### 1. SSH接続
```bash
ssh root@210.131.210.25
```

### 2. リポジトリクローン
```bash
cd /opt
git clone https://github.com/HBM-AKAMATSU/ai-agent-hbm.git ai-agent-hbm
cd ai-agent-hbm
```

## 🔍 ステップ1: 環境調査

```bash
# 事前環境調査（既存サービス確認）
chmod +x pre-deploy-check.sh
./pre-deploy-check.sh
```

**確認項目:**
- ✅ ポート8001が利用可能
- ✅ `/opt/ai-agent-hbm`が利用可能
- ✅ 既存のn8n、Nginxが正常稼働
- ✅ 十分なディスク・メモリ容量

## ⚙️ ステップ2: 環境変数設定

```bash
# 本番用環境変数ファイル作成
cp .env.production .env.production.local

# 環境変数編集
nano .env.production.local
```

**設定必須項目:**
```bash
# 実際の値に置き換えてください
OPENAI_API_KEY=sk-proj-...
LINE_CHANNEL_ACCESS_TOKEN=...
LINE_CHANNEL_SECRET=...
SERPER_API_KEY=...
N8N_WEBHOOK_URL=https://n8n.xvps.jp/webhook-test/hannan-email-webhook
```

## 🚀 ステップ3: 安全デプロイ実行

```bash
# デプロイスクリプト実行
chmod +x deploy-safe.sh
./deploy-safe.sh
```

**このスクリプトの安全機能:**
- 🛡️ 既存サービス自動検出・保護
- 🔍 ポート競合チェック
- 📊 リソース制限設定
- 🚨 エラー時自動停止

## 🌐 ステップ4: Nginx設定追加

```bash
# 既存Nginxに設定追加（上書きしない）
cp nginx-reverse-proxy.conf /etc/nginx/sites-available/ai-agent
ln -s /etc/nginx/sites-available/ai-agent /etc/nginx/sites-enabled/

# 設定テスト（既存設定の破綻チェック）
nginx -t

# 問題なければリロード
systemctl reload nginx
```

## 🔐 ステップ5: SSL証明書設定

```bash
# 新しいサブドメイン用SSL証明書取得
certbot --nginx -d ai.hbm-web.co.jp

# 自動更新テスト
certbot renew --dry-run
```

## ✅ ステップ6: 動作確認

```bash
# 1. ローカルアクセステスト
curl http://localhost:8001/health

# 2. 外部アクセステスト
curl https://ai.hbm-web.co.jp/health

# 3. Docker確認
docker ps | grep hbm-ai-agent

# 4. 既存サービス確認（重要！）
systemctl status nginx
systemctl status n8n
curl https://n8n.xvps.jp  # 既存サイトが正常
```

## 📊 正常稼働の確認

### 期待する結果

#### ヘルスチェック
```json
{
  "status": "healthy",
  "service": {
    "name": "阪南ビジネスマシン Smart Office Assistant",
    "version": "1.0.0"
  },
  "system": {
    "cpu_percent": 10.5,
    "memory_percent": 45.2
  }
}
```

#### ポート使用状況
```bash
netstat -tlnp | grep -E ":(80|443|8001)"
# :80   -> nginx (既存)
# :443  -> nginx (既存)  
# :8001 -> python (新規AIエージェント)
```

## 🛠️ 日常運用

### サービス管理
```bash
cd /opt/ai-agent-hbm

# 状態確認
docker-compose -f docker-compose.safe.yml ps

# ログ監視
docker-compose -f docker-compose.safe.yml logs -f hbm-ai-agent

# 再起動
docker-compose -f docker-compose.safe.yml restart hbm-ai-agent

# 停止（緊急時）
docker-compose -f docker-compose.safe.yml down
```

### 監視コマンド
```bash
# リソース監視
docker stats hbm-ai-agent-app

# 詳細ヘルスチェック
curl -s http://localhost:8001/health | jq '.'

# ログ確認
tail -f /var/log/hbm-ai-agent.log
```

## 🚨 緊急時対応

### 即座停止
```bash
cd /opt/ai-agent-hbm
docker-compose -f docker-compose.safe.yml down
```

### 完全ロールバック
```bash
chmod +x emergency-rollback.sh
./emergency-rollback.sh
```

### 完全削除（必要時のみ）
```bash
./emergency-rollback.sh --remove-all
```

## 📞 アクセス情報

### URL
- **メインサイト**: https://ai.hbm-web.co.jp
- **ヘルスチェック**: https://ai.hbm-web.co.jp/health
- **LINE Webhook**: https://ai.hbm-web.co.jp/webhook

### ポート情報
- **内部**: 8001 (AIエージェント専用)
- **外部**: 443 (HTTPS、既存Nginxを経由)

### ログ場所
- **アプリケーション**: `/opt/ai-agent-hbm/hbm-ai/logs/`
- **デプロイ**: `/var/log/hbm-ai-agent.log`
- **Nginx**: `/var/log/nginx/ai-agent.*.log`

## ⚠️ 重要な注意事項

### 絶対に触らないもの
- ❌ 既存のポート80/443
- ❌ 既存のn8n設定・データ
- ❌ 既存のNginx main設定
- ❌ システムファイアウォール設定

### 使用する専用リソース
- ✅ ポート8001（内部のみ）
- ✅ ディレクトリ `/opt/ai-agent-hbm/`
- ✅ コンテナ名 `hbm-ai-agent-app`
- ✅ ログファイル `/var/log/hbm-ai-agent.log`

## 📈 成功の指標

1. **既存サービス**: n8n.xvps.jp が正常稼働
2. **新サービス**: ai.hbm-web.co.jp が正常稼働  
3. **リソース**: CPU/メモリが適切な範囲
4. **ログ**: エラーが発生していない
5. **LINE**: Webhookが正常動作

---

**🎯 この手順により、既存サービスに一切影響を与えることなくAIエージェントをデプロイできます！**
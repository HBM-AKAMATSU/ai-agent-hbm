# 共有VPSデプロイメントガイド

n8n.xvps.jp (210.131.210.25) 上で既存サービスと競合しない安全なデプロイ方法

## ⚠️ 重要な競合回避事項

### 🚨 既存サービスとの競合リスク
- **n8nサービス**: 既に80/443ポートを使用
- **他のAIエージェント**: 既存のアプリケーションが稼働中
- **Nginx設定**: 既存のリバースプロキシ設定
- **SSL証明書**: Let's Encryptの管理

### ✅ 安全な解決策
1. **専用ポート使用**: 8001番ポート（80/443は使用しない）
2. **独立したコンテナ**: 既存Dockerネットワークとは分離
3. **専用ディレクトリ**: `/opt/ai-agent-hbm`（n8nと区別）
4. **既存Nginx活用**: 新しいserver blockを追加

## 🛡️ 安全デプロイ手順

### ステップ1: 安全デプロイスクリプト実行

```bash
# 共有VPS (n8n.xvps.jp) にログイン
ssh user@n8n.xvps.jp

# リポジトリクローン
sudo git clone https://github.com/HBM-AKAMATSU/ai-agent-hbm.git /opt/ai-agent-hbm
cd /opt/ai-agent-hbm

# 環境変数設定
sudo cp .env.production .env.production.local
sudo nano .env.production.local
# 必要なAPI Keyを設定

# 安全デプロイ実行
sudo chmod +x deploy-safe.sh
sudo ./deploy-safe.sh
```

### ステップ2: 既存Nginxに設定追加

```bash
# Nginx設定ファイル作成
sudo cp /opt/ai-agent-hbm/nginx-reverse-proxy.conf /etc/nginx/sites-available/ai-agent

# サイト有効化
sudo ln -s /etc/nginx/sites-available/ai-agent /etc/nginx/sites-enabled/

# 設定テスト
sudo nginx -t

# Nginx再読み込み（既存サービスに影響なし）
sudo systemctl reload nginx
```

### ステップ3: SSL証明書設定

```bash
# 専用証明書取得
sudo certbot --nginx -d ai.hbm-web.co.jp

# または既存のワイルドカード証明書を使用
# *.hbm-web.co.jp の証明書があれば、そちらを使用推奨
```

## 📋 設定ファイル詳細

### 使用ファイル一覧（競合回避版）

| ファイル | 用途 | 競合回避ポイント |
|---------|-----|-----------------|
| `docker-compose.safe.yml` | 安全なDocker設定 | ポート8001、専用ネットワーク |
| `deploy-safe.sh` | 安全デプロイスクリプト | 既存サービス確認、競合チェック |
| `nginx-reverse-proxy.conf` | Nginx追加設定 | 既存設定に追加のみ |

### ポート使用状況

```bash
# 確認コマンド
sudo netstat -tlnp | grep -E ":(80|443|8001|5678)"

# 期待する結果:
# :80   -> 既存Nginx (n8n用)
# :443  -> 既存Nginx (n8n用)  
# :5678 -> n8n (もしくは他のポート)
# :8001 -> AIエージェント (新規)
```

### ディレクトリ構造（競合回避）

```
/opt/
├── n8n/                    # 既存n8nファイル
├── ai-agent-hbm/          # AIエージェント（新規）
│   ├── hbm-ai/           # 専用データディレクトリ
│   │   ├── logs/
│   │   ├── faiss_index_office/
│   │   └── faiss_index_sales/
│   ├── docker-compose.safe.yml
│   └── deploy-safe.sh
└── ai-agent-hbm_backup/   # バックアップ
```

## 🔍 動作確認

### ローカルテスト

```bash
# ヘルスチェック
curl http://localhost:8001/health

# 期待する結果:
{
  "status": "healthy",
  "service": {
    "name": "阪南ビジネスマシン Smart Office Assistant",
    "version": "1.0.0"
  }
}
```

### 外部アクセステスト

```bash
# HTTPS経由（Nginx設定後）
curl https://ai.hbm-web.co.jp/health

# LINE Webhook テスト
curl -X POST https://ai.hbm-web.co.jp/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

## 🔧 運用・監視

### サービス管理

```bash
# サービス状態確認
cd /opt/ai-agent-hbm
sudo docker-compose -f docker-compose.safe.yml ps

# ログ確認
sudo docker-compose -f docker-compose.safe.yml logs -f hbm-ai-agent

# サービス再起動
sudo docker-compose -f docker-compose.safe.yml restart hbm-ai-agent

# サービス停止（n8nに影響なし）
sudo docker-compose -f docker-compose.safe.yml down
```

### リソース監視

```bash
# システムリソース確認
htop

# Dockerコンテナリソース
docker stats hbm-ai-agent-app

# ログファイル確認
tail -f /var/log/hbm-ai-agent.log
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. ポート競合

```bash
# ポート使用状況確認
sudo netstat -tlnp | grep :8001

# 他のプロセスが使用している場合
sudo kill $(sudo lsof -t -i:8001)
```

#### 2. Docker権限エラー

```bash
# Dockerグループ確認
groups $USER

# Dockerグループに追加（必要に応じて）
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Nginx設定エラー

```bash
# 設定テスト
sudo nginx -t

# エラーがある場合、既存設定との競合を確認
sudo nginx -T | grep -A 5 -B 5 "server_name ai.hbm-web.co.jp"
```

#### 4. SSL証明書問題

```bash
# 証明書確認
sudo certbot certificates

# 更新
sudo certbot renew --dry-run
```

### 既存サービスへの影響確認

```bash
# n8nサービス確認
sudo systemctl status n8n
curl http://localhost:5678  # n8nのデフォルトポート

# 既存Nginx確認
sudo systemctl status nginx
curl http://n8n.xvps.jp  # 既存サービス
```

## 🔒 セキュリティ考慮事項

### ファイアウォール設定

```bash
# 現在のUFW設定確認（変更しない）
sudo ufw status

# 必要に応じて8001ポートを内部からのみ許可
# sudo ufw allow from 127.0.0.1 to any port 8001
```

### ログローテーション

```bash
# AIエージェント専用ログローテーション
sudo tee /etc/logrotate.d/hbm-ai-agent << 'EOF'
/var/log/hbm-ai-agent.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

## 📞 サポート情報

### アクセスURL
- **メインサイト**: https://ai.hbm-web.co.jp
- **ヘルスチェック**: https://ai.hbm-web.co.jp/health
- **LINE Webhook**: https://ai.hbm-web.co.jp/webhook

### ポート情報
- **内部ポート**: 8001（他サービスと競合回避）
- **外部アクセス**: 443（HTTPS、既存Nginxを経由）

### ログ場所
- **アプリケーション**: `/opt/ai-agent-hbm/hbm-ai/logs/`
- **デプロイ**: `/var/log/hbm-ai-agent.log`
- **Nginx**: `/var/log/nginx/ai-agent.*.log`

---

この設定により、既存のn8nや他のサービスに一切影響を与えることなく、AIエージェントを安全にデプロイできます。
# VPSデプロイメントガイド

阪南ビジネスマシン AIエージェント システムのVPSサーバーへのデプロイメント手順

## 📋 目次

1. [システム要件](#システム要件)
2. [事前準備](#事前準備)
3. [VPSサーバーセットアップ](#vpsサーバーセットアップ)
4. [アプリケーションデプロイ](#アプリケーションデプロイ)
5. [SSL証明書設定](#ssl証明書設定)
6. [運用・監視](#運用監視)
7. [トラブルシューティング](#トラブルシューティング)

## 🖥️ システム要件

### 推奨VPSスペック
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 2コア以上
- **メモリ**: 8GB以上（FAISSベクトルDB用）
- **ストレージ**: 50GB以上
- **ネットワーク**: 100Mbps以上

### 必要なソフトウェア
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
- Nginx（Dockerコンテナ内）
- SSL証明書（Let's Encrypt推奨）

## 🔧 事前準備

### 1. ドメイン設定
```bash
# DNSレコードを設定
# 例: ai.hbm-web.co.jp -> VPSのIPアドレス
```

### 2. 環境変数準備
以下のAPIキーを取得：
- OpenAI API Key
- LINE Bot Channel Access Token & Secret
- Serper API Key (Google検索用)

### 3. n8n Webhook URL確認
```bash
# n8nサーバーのWebhook URLを確認
https://n8n.xvps.jp/webhook-test/hannan-email-webhook
```

## 🚀 VPSサーバーセットアップ

### ステップ1: 基本システム設定

```bash
# システム更新
sudo apt update && sudo apt upgrade -y

# 必要パッケージインストール
sudo apt install -y curl wget git ufw fail2ban htop jq

# ファイアウォール設定
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### ステップ2: Docker環境構築

```bash
# Docker公式GPGキー追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Dockerリポジトリ追加
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker & Docker Composeインストール
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Dockerサービス開始・自動起動設定
sudo systemctl start docker
sudo systemctl enable docker

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER
newgrp docker

# インストール確認
docker --version
docker compose version
```

## 📦 アプリケーションデプロイ

### 自動デプロイ（推奨方法）

```bash
# デプロイディレクトリ作成
sudo mkdir -p /opt/hbm-ai-agent
cd /opt/hbm-ai-agent

# リポジトリクローン
sudo git clone https://github.com/HBM-AKAMATSU/ai-agent-hbm.git .

# 本番用環境変数設定
sudo cp .env.production .env.production.backup
sudo nano .env.production

# 以下の値を実際の値に置き換え:
# OPENAI_API_KEY=actual_openai_key_here
# LINE_CHANNEL_ACCESS_TOKEN=actual_line_token_here
# LINE_CHANNEL_SECRET=actual_line_secret_here
# SERPER_API_KEY=actual_serper_key_here

# デプロイスクリプト実行
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

### 手動デプロイ（詳細制御が必要な場合）

```bash
# リポジトリクローン
git clone https://github.com/HBM-AKAMATSU/ai-agent-hbm.git
cd ai-agent-hbm

# 環境変数設定
cp .env.production .env.production.local
nano .env.production.local

# SSL証明書ディレクトリ作成
mkdir -p ssl logs nginx/logs

# Dockerイメージビルド
docker compose build

# ベクトルデータベース構築
docker compose run --rm ai-agent python setup_vector_db.py

# サービス起動
docker compose up -d

# 動作確認
curl http://localhost:8000/health
```

## 🔐 SSL証明書設定

### Let's Encrypt（推奨）

```bash
# Certbot インストール
sudo apt install -y certbot python3-certbot-nginx

# 証明書取得（ドメインを実際の値に置き換え）
sudo certbot certonly --standalone -d ai.hbm-web.co.jp

# 証明書をDockerボリュームにコピー
sudo cp /etc/letsencrypt/live/ai.hbm-web.co.jp/fullchain.pem /opt/hbm-ai-agent/ssl/
sudo cp /etc/letsencrypt/live/ai.hbm-web.co.jp/privkey.pem /opt/hbm-ai-agent/ssl/
sudo chown -R 1000:1000 /opt/hbm-ai-agent/ssl/

# 自動更新設定
sudo crontab -e
# 以下を追加:
# 0 3 * * * certbot renew --quiet && docker compose -f /opt/hbm-ai-agent/docker-compose.yml restart nginx
```

### 自己署名証明書（開発・テスト用）

```bash
cd /opt/hbm-ai-agent/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout privkey.pem \
    -out fullchain.pem \
    -subj "/C=JP/ST=Osaka/L=Osaka/O=HBM/CN=ai.hbm-web.co.jp"
```

## 📊 運用・監視

### サービス管理

```bash
# サービス状態確認
docker compose ps

# ログ確認
docker compose logs -f ai-agent
docker compose logs -f nginx

# サービス再起動
docker compose restart ai-agent

# 設定リロード
docker compose down && docker compose up -d
```

### ヘルスチェック

```bash
# 基本ヘルスチェック
curl -s https://ai.hbm-web.co.jp/health | jq '.'

# 詳細システム情報
curl -s https://ai.hbm-web.co.jp/health | jq '.system'

# 環境変数確認
curl -s https://ai.hbm-web.co.jp/health | jq '.environment'
```

### システム監視

```bash
# リソース使用量監視
htop

# Dockerコンテナ監視
docker stats

# ログ監視
tail -f /var/log/hbm-ai-agent_deploy.log
```

### 自動バックアップ設定

```bash
# バックアップスクリプト作成
sudo tee /opt/backup_ai_agent.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/hbm-ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd /opt/hbm-ai-agent

# ベクトルデータベースバックアップ
tar -czf $BACKUP_DIR/faiss_indexes_$DATE.tar.gz faiss_index_*

# 設定ファイルバックアップ
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env.production docker-compose.yml nginx/

# 古いバックアップ削除（7日以上）
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /opt/backup_ai_agent.sh

# 定期バックアップ設定
sudo crontab -e
# 以下を追加:
# 0 2 * * * /opt/backup_ai_agent.sh
```

## 🐛 トラブルシューティング

### よくある問題と解決法

#### 1. コンテナが起動しない

```bash
# ログ確認
docker compose logs ai-agent

# 環境変数確認
docker compose config

# イメージ再ビルド
docker compose build --no-cache
```

#### 2. メモリ不足エラー

```bash
# メモリ使用量確認
free -h

# スワップ追加
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 3. SSL証明書エラー

```bash
# 証明書有効性確認
openssl x509 -in ssl/fullchain.pem -text -noout

# 証明書更新
sudo certbot renew --force-renewal
```

#### 4. ネットワーク接続問題

```bash
# ポート確認
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# ファイアウォール確認
sudo ufw status verbose

# Docker ネットワーク確認
docker network ls
```

#### 5. ベクトルデータベース問題

```bash
# データベース再構築
docker compose run --rm ai-agent python setup_vector_db.py

# データファイル確認
ls -la faiss_index_office/
ls -la src/data/office_data/
```

### ログ場所

- **アプリケーションログ**: `/opt/hbm-ai-agent/logs/`
- **Nginxログ**: `/opt/hbm-ai-agent/nginx/logs/`
- **デプロイログ**: `/var/log/hbm-ai-agent_deploy.log`
- **Dockerログ**: `docker compose logs`

### 緊急時対応

```bash
# サービス緊急停止
docker compose down

# 前バージョンへロールバック
cd /opt/hbm-ai-agent_backup
docker compose up -d

# データベース復旧
tar -xzf /opt/backups/hbm-ai-agent/faiss_indexes_latest.tar.gz
```

## 📞 サポート情報

- **GitHub**: https://github.com/HBM-AKAMATSU/ai-agent-hbm
- **会社**: 阪南ビジネスマシン株式会社
- **ウェブサイト**: https://hbm-web.co.jp/

## 📝 更新履歴

- **v1.0.0** (2025-08-05): 初回リリース・Docker化対応
- **v1.0.1** (予定): パフォーマンス最適化・監視機能強化
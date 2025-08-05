#!/bin/bash
# n8n_setup_guide.sh
# N8N セットアップガイド

echo "🚀 N8N セットアップガイド"
echo ""

echo "## Step 1: N8Nのインストール"
echo ""
echo "### 方法A: Docker（推奨）"
echo "docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n"
echo ""
echo "### 方法B: npm"
echo "npm install n8n -g"
echo "n8n start"
echo ""

echo "## Step 2: アクセス確認"
echo "ブラウザで http://localhost:5678 にアクセス"
echo ""

echo "## Step 3: 初期設定"
echo "1. 管理者アカウントを作成"
echo "2. ダッシュボードにアクセス"
echo ""

echo "## 🌐 外部アクセス用設定（本番環境）"
echo "### Docker Compose例："
cat << 'EOF'
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password
      - N8N_HOST=your-domain.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://your-domain.com/
    volumes:
      - ~/.n8n:/home/node/.n8n
EOF

echo ""
echo "## 🔐 セキュリティ設定"
echo "1. Basic認証を有効化"
echo "2. HTTPS証明書の設定"
echo "3. ファイアウォール設定"

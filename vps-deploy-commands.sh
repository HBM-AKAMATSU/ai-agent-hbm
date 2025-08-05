#!/bin/bash
# vps-deploy-commands.sh - SSH接続後に実行するコマンド集
# 210.131.210.25 (n8n.xvps.jp) での実行手順

echo "🚀 n8n.xvps.jp デプロイコマンド集"
echo "以下のコマンドを順番に実行してください"
echo "=================================================="

echo ""
echo "📋 ステップ1: 事前環境調査"
echo "------------------------------------------------"
cat << 'EOF'
# リポジトリクローン
cd /opt
git clone https://github.com/HBM-AKAMATSU/ai-agent-hbm.git ai-agent-hbm
cd ai-agent-hbm

# 環境調査実行
chmod +x pre-deploy-check.sh
./pre-deploy-check.sh
EOF

echo ""
echo "📋 ステップ2: 環境変数設定"
echo "------------------------------------------------"
cat << 'EOF'
# 本番用環境変数ファイル作成
cp .env.production .env.production.local

# 環境変数編集（実際の値に置き換え）
nano .env.production.local

# 設定すべき値:
# OPENAI_API_KEY=sk-proj-...（実際のOpenAI APIキー）
# LINE_CHANNEL_ACCESS_TOKEN=（実際のLINE Bot Token）  
# LINE_CHANNEL_SECRET=（実際のLINE Bot Secret）
# SERPER_API_KEY=（実際のSerper APIキー）
# N8N_WEBHOOK_URL=https://n8n.xvps.jp/webhook-test/hannan-email-webhook
EOF

echo ""
echo "📋 ステップ3: 安全デプロイ実行"
echo "------------------------------------------------"
cat << 'EOF'
# デプロイスクリプト実行権限付与
chmod +x deploy-safe.sh

# 競合チェック付きデプロイ実行
./deploy-safe.sh

# 実行結果を確認
# - 既存サービスへの影響がないこと
# - ポート8001でリスニング開始
# - ヘルスチェックが正常
EOF

echo ""
echo "📋 ステップ4: Nginx設定追加"
echo "------------------------------------------------"
cat << 'EOF'
# 既存Nginxに新しいserver blockを追加
cp nginx-reverse-proxy.conf /etc/nginx/sites-available/ai-agent

# サイト有効化
ln -s /etc/nginx/sites-available/ai-agent /etc/nginx/sites-enabled/

# Nginx設定テスト（既存設定の破綻チェック）
nginx -t

# 問題なければNginx設定リロード
systemctl reload nginx
EOF

echo ""
echo "📋 ステップ5: SSL証明書設定"
echo "------------------------------------------------"
cat << 'EOF'
# 新しいサブドメイン用SSL証明書取得
certbot --nginx -d ai.hbm-web.co.jp

# 証明書の自動更新テスト
certbot renew --dry-run
EOF

echo ""
echo "📋 ステップ6: 動作確認"
echo "------------------------------------------------"
cat << 'EOF'
# ローカルアクセステスト
curl http://localhost:8001/health

# 外部アクセステスト（SSL設定後）
curl https://ai.hbm-web.co.jp/health

# Docker コンテナ確認
docker ps | grep hbm-ai-agent

# ログ確認
tail -f /var/log/hbm-ai-agent.log
EOF

echo ""
echo "📋 ステップ7: 既存サービス確認（重要）"
echo "------------------------------------------------"
cat << 'EOF'
# 既存サービスが正常稼働していることを確認
systemctl status nginx
systemctl status n8n  # （存在する場合）

# n8nの動作確認
curl http://localhost:5678  # n8nデフォルトポート
curl https://n8n.xvps.jp    # 外部アクセス

# リソース使用量確認
htop
docker stats
EOF

echo ""
echo "⚠️  緊急時停止コマンド"
echo "------------------------------------------------"
cat << 'EOF'
# 問題が発生した場合の即座停止
cd /opt/ai-agent-hbm
docker-compose -f docker-compose.safe.yml down

# 完全削除（必要に応じて）
docker-compose -f docker-compose.safe.yml down --volumes --rmi all
rm -rf /opt/ai-agent-hbm
EOF

echo ""
echo "🔗 便利なコマンド"
echo "------------------------------------------------"
cat << 'EOF'
# サービス管理
cd /opt/ai-agent-hbm
docker-compose -f docker-compose.safe.yml ps          # 状態確認
docker-compose -f docker-compose.safe.yml logs -f     # ログ監視
docker-compose -f docker-compose.safe.yml restart     # 再起動

# ヘルスチェック
curl -s http://localhost:8001/health | jq '.'         # 詳細ヘルス情報

# リソース監視
docker stats hbm-ai-agent-app                         # コンテナリソース
netstat -tlnp | grep :8001                            # ポート確認
EOF

echo ""
echo "=================================================="
echo "✅ すべてのコマンドが用意されました"
echo "📝 順番に実行して、各ステップで結果を確認してください"
echo "🛡️ 既存サービスへの影響がないことを必ず確認してください"
#!/bin/bash
# emergency-rollback.sh - 緊急時ロールバックスクリプト
# 何か問題が発生した場合の即座復旧用

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}🚨 緊急時ロールバック実行${NC}"
echo "=================================================="

# 1. AIエージェントコンテナ即座停止
echo -e "${YELLOW}⏹️ AIエージェントサービス停止中...${NC}"
cd /opt/ai-agent-hbm 2>/dev/null || cd /opt/hbm-ai-agent 2>/dev/null || {
    echo -e "${RED}❌ デプロイディレクトリが見つかりません${NC}"
    exit 1
}

# Docker Compose停止
if [ -f "docker-compose.safe.yml" ]; then
    docker-compose -f docker-compose.safe.yml down --remove-orphans
    echo -e "${GREEN}✅ 安全版コンテナを停止しました${NC}"
elif [ -f "docker-compose.yml" ]; then
    docker-compose down --remove-orphans
    echo -e "${GREEN}✅ 通常版コンテナを停止しました${NC}"
fi

# 2. Nginxから追加設定を削除
echo -e "${YELLOW}🌐 Nginx設定をロールバック中...${NC}"
if [ -f "/etc/nginx/sites-enabled/ai-agent" ]; then
    rm -f /etc/nginx/sites-enabled/ai-agent
    echo -e "${GREEN}✅ ai-agent サイトを無効化しました${NC}"
fi

if [ -f "/etc/nginx/sites-available/ai-agent" ]; then
    rm -f /etc/nginx/sites-available/ai-agent
    echo -e "${GREEN}✅ ai-agent 設定ファイルを削除しました${NC}"
fi

# Nginx設定テスト & リロード
if nginx -t 2>/dev/null; then
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx設定をリロードしました${NC}"
else
    echo -e "${RED}⚠️ Nginx設定にエラーがあります${NC}"
    systemctl restart nginx
fi

# 3. 使用中ポートの確認と解放
echo -e "${YELLOW}🔌 ポート8001の解放確認中...${NC}"
if netstat -tlnp | grep -q ":8001 "; then
    echo -e "${YELLOW}⚠️ ポート8001がまだ使用中です${NC}"
    # プロセス強制終了
    lsof -ti:8001 | xargs -r kill -9
    sleep 2
    if ! netstat -tlnp | grep -q ":8001 "; then
        echo -e "${GREEN}✅ ポート8001を解放しました${NC}"
    fi
else
    echo -e "${GREEN}✅ ポート8001は既に解放されています${NC}"
fi

# 4. Docker関連リソースクリーンアップ
echo -e "${YELLOW}🐳 Dockerリソースクリーンアップ中...${NC}"

# AIエージェント関連のコンテナ削除
docker ps -a | grep -E "(hbm-ai-agent|ai-agent)" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# AIエージェント関連のイメージ削除（オプション）
if [ "$1" = "--full-cleanup" ]; then
    docker images | grep -E "(hbm-ai-agent|ai-agent)" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    echo -e "${GREEN}✅ AIエージェント関連イメージを削除しました${NC}"
fi

# 専用ネットワーク削除
docker network ls | grep "hbm-ai-network" | awk '{print $1}' | xargs -r docker network rm 2>/dev/null || true

# 5. 既存サービスの状態確認
echo -e "${YELLOW}🔍 既存サービス状態確認中...${NC}"

# Nginx確認
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx: 正常稼働中${NC}"
else
    echo -e "${RED}❌ Nginx: 問題発生 - 再起動を試行${NC}"
    systemctl restart nginx
fi

# n8n確認
if systemctl is-active --quiet n8n 2>/dev/null; then
    echo -e "${GREEN}✅ n8n: 正常稼働中${NC}"
elif docker ps | grep -q n8n; then
    echo -e "${GREEN}✅ n8n: Docker経由で稼働中${NC}"
else
    echo -e "${YELLOW}ℹ️ n8n: 状態不明または未使用${NC}"
fi

# 6. アクセステスト
echo -e "${YELLOW}🌐 外部アクセステスト中...${NC}"

# n8nサイトテスト
if curl -s --connect-timeout 5 https://n8n.xvps.jp > /dev/null; then
    echo -e "${GREEN}✅ n8n.xvps.jp: アクセス正常${NC}"
else
    echo -e "${RED}❌ n8n.xvps.jp: アクセス不可${NC}"
fi

# 7. ログファイルのバックアップ
echo -e "${YELLOW}📋 ログファイルバックアップ中...${NC}"
if [ -f "/var/log/hbm-ai-agent.log" ]; then
    cp /var/log/hbm-ai-agent.log "/var/log/hbm-ai-agent.rollback.$(date +%Y%m%d_%H%M%S).log"
    echo -e "${GREEN}✅ ログファイルをバックアップしました${NC}"
fi

# 8. 完全削除（オプション）
if [ "$1" = "--remove-all" ]; then
    echo -e "${RED}🗑️ 完全削除を実行中...${NC}"
    rm -rf /opt/ai-agent-hbm /opt/hbm-ai-agent 2>/dev/null || true
    echo -e "${GREEN}✅ デプロイディレクトリを削除しました${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 緊急時ロールバック完了${NC}"
echo ""
echo -e "${YELLOW}📋 実行した内容:${NC}"
echo "• AIエージェントコンテナ停止・削除"
echo "• Nginx設定をロールバック"
echo "• ポート8001を解放"
echo "• Dockerリソースクリーンアップ"
echo "• 既存サービス動作確認"
echo ""
echo -e "${YELLOW}📋 確認事項:${NC}"
echo "• n8n.xvps.jp にアクセスできること"
echo "• 既存サービスが正常動作していること"
echo "• システムリソースが正常範囲内であること"
echo ""
echo -e "${BLUE}💡 オプション:${NC}"
echo "• 完全クリーンアップ: ./emergency-rollback.sh --full-cleanup"
echo "• ファイル削除含む: ./emergency-rollback.sh --remove-all"
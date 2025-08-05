#!/bin/bash
# pre-deploy-check.sh - デプロイ前環境調査スクリプト
# 210.131.210.25 (n8n.xvps.jp) での既存サービス調査

set -e

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 n8n.xvps.jp (210.131.210.25) 環境調査開始"
echo "=================================================="

# 1. システム基本情報
echo ""
echo -e "${BLUE}📊 システム基本情報${NC}"
echo "ホスト名: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "カーネル: $(uname -r)"
echo "アーキテクチャ: $(uname -m)"

# 2. 使用中ポート確認（重要）
echo ""
echo -e "${BLUE}🔌 使用中ポート確認${NC}"
echo "重要ポートの使用状況:"
netstat -tlnp | grep -E ":(80|443|5678|8000|8001|3000|4000)" | while read line; do
    port=$(echo $line | awk '{print $4}' | cut -d':' -f2)
    process=$(echo $line | awk '{print $7}')
    if [ "$port" = "80" ] || [ "$port" = "443" ]; then
        echo -e "  ${RED}ポート $port: $process (Nginx/Web)${NC}"
    elif [ "$port" = "8001" ]; then
        echo -e "  ${RED}⚠️ ポート $port: $process (競合リスク！)${NC}"
    else
        echo -e "  ${YELLOW}ポート $port: $process${NC}"
    fi
done

# 3. 実行中サービス確認
echo ""
echo -e "${BLUE}🔄 実行中サービス確認${NC}"
echo "重要サービスの状態:"
services=("nginx" "n8n" "docker" "postgresql" "mysql" "redis")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "  ${GREEN}✅ $service: 稼働中${NC}"
    elif systemctl list-unit-files | grep -q "^$service.service"; then
        echo -e "  ${YELLOW}⏸️ $service: 停止中${NC}"
    else
        echo -e "  ${BLUE}ℹ️ $service: 未インストール${NC}"
    fi
done

# 4. Docker環境確認
echo ""
echo -e "${BLUE}🐳 Docker環境確認${NC}"
if command -v docker &> /dev/null; then
    echo "Docker Version: $(docker --version)"
    echo "実行中コンテナ:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}" | head -10
    
    echo ""
    echo "Dockerネットワーク:"
    docker network ls
else
    echo -e "${RED}❌ Docker未インストール${NC}"
fi

# 5. Nginx設定確認
echo ""
echo -e "${BLUE}🌐 Nginx設定確認${NC}"
if systemctl is-active --quiet nginx; then
    echo "Nginx設定ファイル:"
    find /etc/nginx/sites-enabled -name "*.conf" -o -name "*" -type f 2>/dev/null | head -5
    
    echo ""
    echo "Virtual Hosts:"
    nginx -T 2>/dev/null | grep "server_name" | sort | uniq | head -5
else
    echo "Nginxが稼働していません"
fi

# 6. ディスク・メモリ使用量
echo ""
echo -e "${BLUE}💾 リソース使用状況${NC}"
echo "ディスク使用量:"
df -h | grep -E "(Filesystem|/dev/|tmpfs)" | head -5

echo ""
echo "メモリ使用量:"
free -h

echo ""
echo "CPU情報:"
echo "CPU数: $(nproc)"
echo "平均負荷: $(uptime | awk -F'load average:' '{print $2}')"

# 7. 利用可能ディレクトリ確認
echo ""
echo -e "${BLUE}📁 デプロイディレクトリ確認${NC}"
deploy_dirs=("/opt" "/home" "/var/www")
for dir in "${deploy_dirs[@]}"; do
    if [ -d "$dir" ] && [ -w "$dir" ]; then
        space=$(df -h "$dir" | tail -1 | awk '{print $4}')
        echo -e "  ${GREEN}✅ $dir (利用可能容量: $space)${NC}"
    else
        echo -e "  ${RED}❌ $dir (アクセス不可)${NC}"
    fi
done

# 8. ファイアウォール確認
echo ""
echo -e "${BLUE}🔥 ファイアウォール確認${NC}"
if command -v ufw &> /dev/null; then
    echo "UFW状態:"
    ufw status
else
    echo "UFW未インストール"
fi

if command -v iptables &> /dev/null; then
    echo ""
    echo "iptables ルール数:"
    iptables -L | wc -l
fi

# 9. SSL証明書確認
echo ""
echo -e "${BLUE}🔐 SSL証明書確認${NC}"
if [ -d "/etc/letsencrypt/live" ]; then
    echo "Let's Encrypt証明書:"
    ls -la /etc/letsencrypt/live/ 2>/dev/null | head -5
else
    echo "Let's Encrypt証明書なし"
fi

# 10. プロセス確認
echo ""
echo -e "${BLUE}⚙️ 重要プロセス確認${NC}"
echo "メモリ使用量トップ5:"
ps aux --sort=-%mem | head -6

# 11. 競合リスク評価
echo ""
echo -e "${YELLOW}⚠️ 競合リスク評価${NC}"
echo "=================================================="

# ポート8001チェック
if netstat -tlnp | grep -q ":8001 "; then
    echo -e "${RED}🚨 危険: ポート8001が使用中 - 別ポートが必要${NC}"
else
    echo -e "${GREEN}✅ 安全: ポート8001は利用可能${NC}"
fi

# /opt/ai-agent-hbm チェック
if [ -d "/opt/ai-agent-hbm" ]; then
    echo -e "${YELLOW}⚠️ 注意: /opt/ai-agent-hbm が既存${NC}"
else
    echo -e "${GREEN}✅ 安全: /opt/ai-agent-hbm は利用可能${NC}"
fi

# Dockerネットワーク172.25.0.0チェック
if docker network ls | grep -q "172.25."; then
    echo -e "${YELLOW}⚠️ 注意: 172.25.x.x ネットワークが既存${NC}"
else
    echo -e "${GREEN}✅ 安全: 172.25.x.x ネットワークは利用可能${NC}"
fi

echo ""
echo -e "${GREEN}🔍 環境調査完了${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📋 推奨次ステップ:${NC}"
echo "1. 問題がなければ deploy-safe.sh を実行"
echo "2. 競合リスクがある場合は設定を調整"
echo "3. 既存サービスの動作を再確認"
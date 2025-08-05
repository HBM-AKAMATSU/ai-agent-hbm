#!/bin/bash
# deploy-safe.sh - 共有VPS安全デプロイスクリプト
# n8n.xvps.jp上で既存サービスと競合しない安全なデプロイ

set -e

# ===========================================
# 設定（競合回避）
# ===========================================
PROJECT_NAME="hbm-ai-agent"
REPOSITORY_URL="https://github.com/HBM-AKAMATSU/ai-agent-hbm.git"
DEPLOY_DIR="/opt/ai-agent-hbm"  # n8nと区別
BACKUP_DIR="/opt/ai-agent-hbm_backup"
LOG_FILE="/var/log/hbm-ai-agent.log"  # 専用ログファイル
SERVICE_PORT="8001"  # n8nと競合しないポート

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===========================================
# ログ関数
# ===========================================
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "${LOG_FILE}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "${LOG_FILE}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "${LOG_FILE}"
}

# ===========================================
# 共有環境チェック
# ===========================================
check_shared_environment() {
    log "🔍 共有環境での競合をチェック中..."
    
    # n8nサービスの確認
    if systemctl is-active --quiet n8n 2>/dev/null; then
        info "✅ n8nサービスが稼働中です"
    else
        warn "n8nサービスが見つかりません"
    fi
    
    # ポート使用状況確認
    if netstat -tlnp | grep -q ":80 "; then
        info "ポート80は使用中（既存Nginx）"
    fi
    
    if netstat -tlnp | grep -q ":443 "; then
        info "ポート443は使用中（既存Nginx）"
    fi
    
    if netstat -tlnp | grep -q ":${SERVICE_PORT} "; then
        error "ポート${SERVICE_PORT}が使用中です。他のポートを選択してください"
    else
        log "✅ ポート${SERVICE_PORT}は利用可能です"
    fi
    
    # Docker確認
    if ! command -v docker &> /dev/null; then
        error "Dockerがインストールされていません"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Composeがインストールされていません"
    fi
    
    log "✅ 共有環境チェック完了"
}

# ===========================================
# 安全なセットアップ
# ===========================================
safe_setup() {
    log "🛡️ 共存安全セットアップを実行中..."
    
    # 専用ディレクトリ作成
    mkdir -p "${DEPLOY_DIR}"
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    # 既存のファイアウォール設定を保持
    # UFWを触らずに済むようにする
    
    log "✅ 安全セットアップ完了"
}

# ===========================================
# リポジトリ更新
# ===========================================
update_repository() {
    log "📦 リポジトリを更新中..."
    
    if [[ -d "${DEPLOY_DIR}/.git" ]]; then
        info "既存リポジトリを更新中..."
        cd "${DEPLOY_DIR}"
        git fetch origin
        git reset --hard origin/main
    else
        info "リポジトリをクローン中..."
        rm -rf "${DEPLOY_DIR}"
        git clone "${REPOSITORY_URL}" "${DEPLOY_DIR}"
        cd "${DEPLOY_DIR}"
    fi
    
    log "✅ リポジトリ更新完了"
}

# ===========================================
# 安全な環境設定
# ===========================================
safe_environment_setup() {
    log "🔧 安全な環境設定中..."
    
    cd "${DEPLOY_DIR}"
    
    # .env.productionの設定
    if [[ ! -f ".env.production" ]]; then
        cp ".env.production" ".env.production.example"
        error "⚠️ .env.productionを設定してから再実行してください"
    fi
    
    # 専用データディレクトリ作成
    mkdir -p hbm-ai/logs
    mkdir -p hbm-ai/data
    mkdir -p hbm-ai/faiss_index_office
    mkdir -p hbm-ai/faiss_index_sales
    mkdir -p hbm-ai/faiss_index_procedures
    
    log "✅ 安全な環境設定完了"
}

# ===========================================
# 安全デプロイ
# ===========================================
safe_deploy() {
    log "🚀 安全デプロイを実行中..."
    
    cd "${DEPLOY_DIR}"
    
    # 安全な設定ファイルを使用
    info "安全な設定ファイル（docker-compose.safe.yml）を使用します"
    
    # 既存のAIエージェントコンテナのみ停止
    docker-compose -f docker-compose.safe.yml down --remove-orphans || true
    
    # イメージビルド
    info "Dockerイメージをビルド中..."
    docker-compose -f docker-compose.safe.yml build --no-cache
    
    # ベクトルデータベース準備
    if [[ ! -f "hbm-ai/faiss_index_office/index.faiss" ]]; then
        info "ベクトルデータベースを構築中..."
        docker-compose -f docker-compose.safe.yml run --rm hbm-ai-agent python setup_vector_db.py
    fi
    
    # サービス起動
    info "サービスを起動中（ポート${SERVICE_PORT}）..."
    docker-compose -f docker-compose.safe.yml up -d
    
    # ヘルスチェック
    info "ヘルスチェックを実行中..."
    for i in {1..30}; do
        if curl -sf http://localhost:${SERVICE_PORT}/health > /dev/null; then
            log "✅ アプリケーション起動確認完了"
            break
        fi
        
        if [[ $i -eq 30 ]]; then
            error "❌ アプリケーションが起動しませんでした"
        fi
        
        info "起動待機中... ($i/30)"
        sleep 10
    done
    
    log "✅ 安全デプロイ完了"
}

# ===========================================
# Nginx設定追加の案内
# ===========================================
nginx_configuration_guide() {
    log "📝 Nginx設定追加ガイド"
    
    echo ""
    echo "========================================"
    echo "🔧 既存Nginxへの設定追加が必要です"
    echo "========================================"
    echo ""
    echo "1. 以下のファイルを既存のNginx設定に追加してください:"
    echo "   ${DEPLOY_DIR}/nginx-reverse-proxy.conf"
    echo ""
    echo "2. 追加場所（推奨）:"
    echo "   /etc/nginx/sites-available/ai-agent"
    echo ""
    echo "3. 有効化コマンド:"
    echo "   sudo ln -s /etc/nginx/sites-available/ai-agent /etc/nginx/sites-enabled/"
    echo "   sudo nginx -t"
    echo "   sudo systemctl reload nginx"
    echo ""
    echo "4. SSL証明書（推奨）:"
    echo "   sudo certbot --nginx -d ai.hbm-web.co.jp"
    echo ""
    echo "⚠️  既存のn8n設定には影響しません"
    echo "========================================"
    echo ""
}

# ===========================================
# 完了確認
# ===========================================
verify_safe_deployment() {
    log "🔍 安全デプロイ確認中..."
    
    # サービス状態確認
    docker-compose -f docker-compose.safe.yml ps
    
    # ローカルアクセステスト
    info "ローカルアクセステスト中..."
    if curl -s http://localhost:${SERVICE_PORT}/health > /dev/null; then
        log "✅ ローカルアクセス正常"
    else
        warn "❌ ローカルアクセスに問題があります"
    fi
    
    # ポート確認
    if netstat -tlnp | grep -q ":${SERVICE_PORT} "; then
        log "✅ ポート${SERVICE_PORT}でリスニング中"
    else
        warn "❌ ポート${SERVICE_PORT}がリスニングしていません"
    fi
    
    log "✅ 安全デプロイ確認完了"
}

# ===========================================
# メイン実行
# ===========================================
main() {
    log "🤖 阪南ビジネスマシン AIエージェント 安全デプロイ開始"
    log "🏠 共有VPS: n8n.xvps.jp (210.131.210.25)"
    log "========================================================"
    
    check_shared_environment
    safe_setup
    update_repository
    safe_environment_setup
    safe_deploy
    nginx_configuration_guide
    verify_safe_deployment
    
    log "========================================================"
    log "🎉 安全デプロイが正常に完了しました！"
    log "🏠 サーバー: n8n.xvps.jp"
    log "📍 ポート: ${SERVICE_PORT}"
    log "💡 ローカルテスト: curl http://localhost:${SERVICE_PORT}/health"
    log "🔗 Nginx設定追加後: https://ai.hbm-web.co.jp"
    log "========================================================"
}

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
#!/bin/bash
# deploy.sh - 阪南ビジネスマシン AIエージェント 自動デプロイスクリプト

set -e

# ===========================================
# 設定
# ===========================================
PROJECT_NAME="hbm-ai-agent"
REPOSITORY_URL="https://github.com/HBM-AKAMATSU/ai-agent-hbm.git"
DEPLOY_DIR="/opt/${PROJECT_NAME}"
BACKUP_DIR="/opt/${PROJECT_NAME}_backup"
LOG_FILE="/var/log/${PROJECT_NAME}_deploy.log"

# カラー設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
# 前提条件チェック
# ===========================================
check_prerequisites() {
    log "🔍 システム前提条件をチェック中..."
    
    # root権限チェック
    if [[ $EUID -ne 0 ]]; then
        error "このスクリプトはroot権限で実行してください: sudo $0"
    fi
    
    # Docker & Docker Composeチェック
    if ! command -v docker &> /dev/null; then
        error "Dockerがインストールされていません"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Composeがインストールされていません"
    fi
    
    # Gitチェック
    if ! command -v git &> /dev/null; then
        error "Gitがインストールされていません"
    fi
    
    log "✅ 前提条件チェック完了"
}

# ===========================================
# 初回セットアップ
# ===========================================
initial_setup() {
    log "🏗️ 初回セットアップを実行中..."
    
    # システムパッケージ更新
    info "システムパッケージを更新中..."
    apt-get update && apt-get upgrade -y
    
    # 必要なパッケージインストール
    apt-get install -y curl wget git ufw fail2ban htop
    
    # ディレクトリ作成
    mkdir -p "${DEPLOY_DIR}"
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    # ファイアウォール設定
    info "ファイアウォールを設定中..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    log "✅ 初回セットアップ完了"
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
        git reset --hard origin/main  # 強制更新
    else
        info "リポジトリをクローン中..."
        rm -rf "${DEPLOY_DIR}"
        git clone "${REPOSITORY_URL}" "${DEPLOY_DIR}"
        cd "${DEPLOY_DIR}"
    fi
    
    log "✅ リポジトリ更新完了"
}

# ===========================================
# 環境設定確認
# ===========================================
check_environment() {
    log "🔧 環境設定をチェック中..."
    
    cd "${DEPLOY_DIR}"
    
    # .env.productionの存在確認
    if [[ ! -f ".env.production" ]]; then
        warn ".env.productionが見つかりません。テンプレートをコピーします..."
        cp ".env.production" ".env.production.example"
        error "⚠️ .env.productionを適切に設定してから再実行してください"
    fi
    
    # 必須環境変数チェック
    if ! grep -q "your_.*_here" ".env.production"; then
        log "✅ 環境変数設定確認完了"
    else
        warn "⚠️ .env.productionに未設定の変数があります。確認してください"
    fi
    
    # SSL証明書ディレクトリ作成
    mkdir -p ssl logs nginx/logs
    
    log "✅ 環境設定チェック完了"
}

# ===========================================
# データベース準備
# ===========================================
prepare_databases() {
    log "🗄️ データベースを準備中..."
    
    cd "${DEPLOY_DIR}"
    
    # 既存のベクトルデータベースをバックアップ
    if [[ -d "faiss_index_office" ]]; then
        info "既存データベースをバックアップ中..."
        cp -r faiss_index_office "${BACKUP_DIR}/faiss_index_office_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # データベース構築（初回またはデータが不足している場合）
    if [[ ! -d "faiss_index_office" ]] || [[ ! -f "faiss_index_office/index.faiss" ]]; then
        info "ベクトルデータベースを構築中..."
        docker-compose -f docker-compose.yml run --rm ai-agent python setup_vector_db.py
    fi
    
    log "✅ データベース準備完了"
}

# ===========================================
# SSL証明書設定
# ===========================================
setup_ssl() {
    log "🔐 SSL証明書を設定中..."
    
    if [[ ! -f "ssl/fullchain.pem" ]] || [[ ! -f "ssl/privkey.pem" ]]; then
        warn "SSL証明書が見つかりません"
        info "Let's Encryptで証明書を取得することを推奨します:"
        info "certbot --nginx -d ai.hbm-web.co.jp"
        
        # 開発用自己署名証明書を生成
        info "開発用自己署名証明書を生成中..."
        mkdir -p ssl
        cd ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout privkey.pem \
            -out fullchain.pem \
            -subj "/C=JP/ST=Osaka/L=Osaka/O=HBM/CN=ai.hbm-web.co.jp"
        cd ..
        warn "⚠️ 本番環境では必ず正式なSSL証明書を使用してください"
    fi
    
    log "✅ SSL証明書設定完了"
}

# ===========================================
# アプリケーションデプロイ
# ===========================================
deploy_application() {
    log "🚀 アプリケーションをデプロイ中..."
    
    cd "${DEPLOY_DIR}"
    
    # 既存コンテナ停止・削除
    info "既存サービスを停止中..."
    docker-compose down --remove-orphans || true
    
    # イメージビルド
    info "Dockerイメージをビルド中..."
    docker-compose build --no-cache
    
    # サービス起動
    info "サービスを起動中..."
    docker-compose up -d
    
    # ヘルスチェック
    info "ヘルスチェックを実行中..."
    for i in {1..30}; do
        if curl -sf http://localhost:8000/health > /dev/null; then
            log "✅ アプリケーション起動確認完了"
            break
        fi
        
        if [[ $i -eq 30 ]]; then
            error "❌ アプリケーションが起動しませんでした"
        fi
        
        info "起動待機中... ($i/30)"
        sleep 10
    done
    
    log "✅ アプリケーションデプロイ完了"
}

# ===========================================
# 監視・ログ設定
# ===========================================
setup_monitoring() {
    log "📊 監視・ログ設定中..."
    
    # logrotate設定
    cat > /etc/logrotate.d/${PROJECT_NAME} << EOF
${LOG_FILE} {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    # Dockerログ制限
    if [[ ! -f /etc/docker/daemon.json ]]; then
        cat > /etc/docker/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
        systemctl restart docker
    fi
    
    log "✅ 監視・ログ設定完了"
}

# ===========================================
# 自動起動設定
# ===========================================
setup_autostart() {
    log "🔄 自動起動を設定中..."
    
    # systemdサービス作成
    cat > /etc/systemd/system/${PROJECT_NAME}.service << EOF
[Unit]
Description=HBM AI Agent
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=${DEPLOY_DIR}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable ${PROJECT_NAME}
    
    log "✅ 自動起動設定完了"
}

# ===========================================
# デプロイ完了確認
# ===========================================
verify_deployment() {
    log "🔍 デプロイ完了確認中..."
    
    # サービス状態確認
    docker-compose ps
    
    # ヘルスチェック詳細
    info "詳細ヘルスチェック実行中..."
    curl -s http://localhost:8000/health | jq '.' || echo "jqが利用できません"
    
    # ログ確認
    info "最新ログ確認中..."
    docker-compose logs --tail=10 ai-agent
    
    log "✅ デプロイ完了確認終了"
}

# ===========================================
# メイン実行
# ===========================================
main() {
    log "🤖 阪南ビジネスマシン AIエージェント デプロイ開始"
    log "========================================================"
    
    check_prerequisites
    
    # 初回セットアップ（必要に応じて）
    if [[ ! -d "${DEPLOY_DIR}" ]]; then
        initial_setup
    fi
    
    update_repository
    check_environment
    setup_ssl
    prepare_databases
    deploy_application
    setup_monitoring
    setup_autostart
    verify_deployment
    
    log "========================================================"
    log "🎉 デプロイが正常に完了しました！"
    log "📍 アクセスURL: https://ai.hbm-web.co.jp"
    log "💡 ヘルスチェック: https://ai.hbm-web.co.jp/health"
    log "📋 ログ確認: docker-compose -f ${DEPLOY_DIR}/docker-compose.yml logs -f"
    log "========================================================"
}

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
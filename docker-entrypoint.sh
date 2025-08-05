#!/bin/bash
# Docker Entrypoint Script for HBM AI Agent

set -e

echo "🤖 阪南ビジネスマシン AIエージェント Docker起動中..."

# 環境変数の確認
echo "📋 環境変数チェック..."
required_vars=("OPENAI_API_KEY" "LINE_CHANNEL_ACCESS_TOKEN" "LINE_CHANNEL_SECRET" "SERPER_API_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 必須環境変数 $var が設定されていません"
        exit 1
    else
        echo "✅ $var: 設定済み"
    fi
done

# データディレクトリの確認
echo "📁 データディレクトリチェック..."
if [ ! -d "/app/faiss_index_office" ] || [ ! "$(ls -A /app/faiss_index_office 2>/dev/null)" ]; then
    echo "🏗️ ベクトルデータベースが見つかりません。初期化します..."
    
    # データファイルの存在確認
    if [ ! -d "/app/data" ] || [ ! "$(ls -A /app/data 2>/dev/null)" ]; then
        echo "⚠️ データファイルがマウントされていません。空のデータベースで起動します。"
    fi
    
    # ベクトルデータベース構築
    echo "🔧 ベクトルデータベース構築中..."
    python setup_vector_db.py
    
    if [ $? -eq 0 ]; then
        echo "✅ ベクトルデータベースの構築が完了しました"
    else
        echo "❌ ベクトルデータベースの構築に失敗しました"
        exit 1
    fi
else
    echo "✅ ベクトルデータベースが存在します"
fi

# ログディレクトリの準備
mkdir -p /app/logs
echo "✅ ログディレクトリを準備しました"

# Pythonパス設定確認
export PYTHONPATH=/app:$PYTHONPATH

echo "🚀 AIエージェントサーバーを起動します..."
echo "📍 Port: 8000"
echo "🏥 Company: 阪南ビジネスマシン株式会社"
echo "💼 Service: Smart Office Assistant"

# 引数を実行
exec "$@"
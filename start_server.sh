#!/bin/bash

# AIエージェントサーバー起動スクリプト

echo "🤖 阪南ビジネスマシン AIエージェント起動中..."

# プロジェクトディレクトリに移動
cd /Users/akamatsu/Desktop/ai-agent

# Conda環境の有効化（Condaを使用している場合）
if command -v conda &> /dev/null; then
    echo "📦 Conda環境を有効化しています..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate office-ai
else
    echo "🐍 Python仮想環境を有効化しています..."
    source venv/bin/activate
fi

# 環境変数の確認
if [ ! -f .env ]; then
    echo "❌ .envファイルが見つかりません。.env.exampleをコピーして.envを作成してください。"
    exit 1
fi

# データベースの存在確認
if [ ! -d "faiss_index_office" ]; then
    echo "🔧 ベクトルデータベースを構築しています..."
    python3 setup_vector_db.py
fi

# サーバー起動
echo "🚀 サーバーを起動しています..."
echo "📍 http://localhost:8000 でアクセスできます"
echo "🛑 停止するには Ctrl+C を押してください"

python3 src/main.py

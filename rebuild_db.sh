#!/bin/bash
# データベース再構築スクリプト

echo "🔧 データベースを再構築中..."

# ai-agentディレクトリに移動
cd /Users/akamatsu/Desktop/ai-agent

# 仮想環境を有効化
source venv/bin/activate

# データベース再構築実行
python setup_vector_db.py

echo "✅ データベース再構築完了"
echo "💡 次にサーバーを再起動してください："
echo "   cd src && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

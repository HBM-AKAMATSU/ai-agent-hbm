#!/bin/bash

echo "🔧 手続きデータベースを作成中..."

# ai-agentディレクトリに移動
cd /Users/akamatsu/Desktop/ai-agent

# 仮想環境を有効化
source venv/bin/activate

# Python環境の確認
echo "📦 Python環境確認..."
python -c "import sys; print(f'Python: {sys.executable}')"
python -c "from dotenv import load_dotenv; print('✅ dotenv OK')"
python -c "from langchain_openai import OpenAIEmbeddings; print('✅ langchain OK')"

# データベース作成実行
echo "🔄 データベース作成開始..."
python create_procedures_db.py

echo "✅ データベース作成完了"
echo ""
echo "💡 次にサーバーを再起動してください："
echo "   1. 現在のサーバーを停止 (Ctrl+C)"
echo "   2. cd src"
echo "   3. uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

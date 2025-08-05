# Dockerfile - 阪南ビジネスマシン AIエージェント
# Multi-stage build for optimized production image

# ===== BUILD STAGE =====
FROM python:3.9-slim as builder

# 作業ディレクトリ設定
WORKDIR /app

# システム依存関係のインストール（ビルド用）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libc6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ===== PRODUCTION STAGE =====
FROM python:3.9-slim as production

# メタデータ
LABEL maintainer="阪南ビジネスマシン株式会社"
LABEL description="Smart Office Assistant AI Agent"
LABEL version="1.0"

# 非rootユーザー作成
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 作業ディレクトリ設定
WORKDIR /app

# システム依存関係のインストール（実行用のみ）
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ビルドステージからPython依存関係をコピー
COPY --from=builder /root/.local /home/appuser/.local

# アプリケーションファイルをコピー
COPY src/ ./src/
COPY setup_vector_db.py .
COPY requirements.txt .

# データディレクトリの作成（マウントポイント）
RUN mkdir -p /app/faiss_index_office \
    /app/faiss_index_sales \
    /app/faiss_index_procedures \
    /app/data \
    /app/logs \
    && chown -R appuser:appuser /app

# 環境変数設定
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ヘルスチェック設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ユーザー切り替え
USER appuser

# ポート公開
EXPOSE 8000

# エントリーポイントスクリプト作成
COPY --chown=appuser:appuser docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# アプリケーション起動
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "src/main.py"]
# Smart Hospital AI Assistant

医療現場向けAIアシスタント - LINEボットによる事務・医療情報検索システム

## 📋 概要

このシステムは、病院職員が日常業務で必要な情報を、LINEを通じて素早く検索・確認できるAIアシスタントです。

### 主な機能
- 🏥 **医療情報検索**: 薬剤情報、用法用量、副作用、相互作用の確認
- 📋 **事務情報検索**: 院内規定、手続き方法、連絡先の照会
- ✅ **ダブルチェック機能**: 投薬前の安全確認支援
- 🤖 **自動分類**: 質問内容を自動判別して適切な回答を提供

## 🛠️ 技術スタック

- **Python 3.11**
- **FastAPI**: WebAPIフレームワーク
- **LangChain**: AI処理・RAG実装
- **OpenAI API**: GPT-4モデル・埋め込みベクトル生成
- **FAISS**: ベクトルデータベース
- **LINE Messaging API**: LINEボット機能
- **Conda**: 環境管理

## 📦 環境構築手順

### 1. 事前準備

#### 必要なAPIキーの取得
1. **OpenAI API**
   - [OpenAI Platform](https://platform.openai.com/)でアカウント作成
   - APIキーを生成
   - 課金設定を完了

2. **LINE Messaging API**
   - [LINE Developers](https://developers.line.biz/)でチャンネル作成
   - Channel Access TokenとChannel Secretを取得

### 2. プロジェクトのクローン・移動

```bash
# プロジェクトフォルダに移動
cd /path/to/smart-hospital-work
```

### 3. Conda環境の構築

```bash
# 1. Conda環境の作成
conda create --name hospital-ai python=3.11 -y

# 2. 環境の有効化
conda activate hospital-ai
# ターミナルが (hospital-ai) から始まることを確認

# 3. FAISSのインストール
conda install -c pytorch faiss-cpu -y

# 4. その他ライブラリのインストール
pip install -r requirements.txt

# 5. OpenAI関連ライブラリの追加インストール
pip install openai langchain-openai tiktoken
```

### 4. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下を設定：

```env
# OpenAI API
OPENAI_API_KEY=sk-your_openai_api_key_here

# LINE Bot API
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# その他（オプション）
GEMINI_API_KEY=your_gemini_api_key
N8N_WEBHOOK_URL=
```

### 5. データベースの構築

```bash
# 古いデータベースがある場合は削除
rm -rf faiss_index_admin
rm -rf faiss_index_medical

# ベクトルデータベースの作成
python3 setup_vector_db.py
```

成功すると以下のメッセージが表示されます：
```
✅ 事務規定データベースを 'faiss_index_admin' フォルダに保存しました。
✅ 医薬品情報データベースを 'faiss_index_medical' フォルダに保存しました。
すべての処理が完了しました。
```

### 6. アプリケーションの起動

```bash
# サーバー起動
python3 src/main.py
```

成功すると以下のメッセージが表示されます：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 7. ngrokによる外部公開（LINEボット用）

別ターミナルで：
```bash
# ngrokのインストール（未インストールの場合）
# https://ngrok.com/ からダウンロード

# ポート8000を外部公開
ngrok http 8000
```

ngrokのURL（例：`https://abc123.ngrok.io`）をLINE DevelopersのWebhook URLに設定：
```
https://abc123.ngrok.io/webhook
```

## 📁 プロジェクト構造

```
smart-hospital-work/
├── README.md
├── requirements.txt
├── setup_vector_db.py          # データベース構築スクリプト
├── .env                        # 環境変数（要作成）
├── faiss_index_admin/          # 事務データベース（自動生成）
├── faiss_index_medical/        # 医療データベース（自動生成）
└── src/
    ├── main.py                 # メインアプリケーション
    ├── config.py               # 設定管理
    ├── data/
    │   ├── admin_docs/         # 事務規定文書（.md形式）
    │   ├── medical_docs/       # 医薬品情報文書（.md形式）
    │   └── dummy_data/
    │       └── patients.json   # ダミー患者データ
    └── services/
        ├── router.py           # 質問分類サービス
        ├── rag_service.py      # RAG検索サービス
        ├── double_check.py     # ダブルチェックサービス
        └── n8n_connector.py    # N8N連携（オプション）
```

## 🔧 トラブルシューティング

### よくあるエラーと解決方法

#### 1. `ModuleNotFoundError: No module named 'langchain_openai'`
```bash
pip install langchain-openai
```

#### 2. `AttributeError: type object 'Config' has no attribute 'OPENAI_API_KEY'`
- `.env` ファイルにOPENAI_API_KEYが設定されているか確認
- `config.py` にOPENAI_API_KEYの定義があるか確認

#### 3. `404 models/gemini-1.0-pro is not found`
- コードがGemini API を参照している場合、OpenAI版に修正が必要
- 本READMEの手順通りに環境構築すればOpenAI版になります

#### 4. 依存関係の競合エラー
```bash
# 環境を完全にリセット
conda deactivate
conda env remove --name hospital-ai
# 再度「3. Conda環境の構築」から実行
```

#### 5. LangChainの警告メッセージ
以下の警告は動作に影響しませんが、importを修正することで解消できます：
```python
# 修正前
from langchain.vectorstores import FAISS
# 修正後
from langchain_community.vectorstores import FAISS
```

## 🧪 動作確認

### 1. LINEボットのテスト

LINEで以下のメッセージを送信してテスト：

**医療関連の質問例：**
- 「ワーファリンの初回投与量を教えて」
- 「P-001にワーファリン処方予定、チェックお願いします」

**事務関連の質問例：**
- 「学会参加費の精算方法を教えて」
- 「薬剤部の内線番号を教えて」

### 2. 期待される動作

- 質問送信後、数秒以内に適切な回答が返される
- 質問内容に応じて事務・医療・ダブルチェック機能が自動選択される
- 関連文書から抽出された具体的で実用的な情報が提供される

## 📄 ライセンス

このプロジェクトは医療現場での業務効率化を目的として開発されています。
商用利用時は適切なライセンス確認を行ってください。

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. 全ての環境変数が正しく設定されているか
2. 必要なAPIキーが有効で、課金設定が完了しているか  
3. Conda環境が正しく有効化されているか（ターミナルに`(hospital-ai)`表示）
4. データベース構築が成功しているか（faiss_index_*フォルダの存在確認）

---

**開発環境**: macOS (Apple Silicon), Python 3.11, Conda
**最終更新**: 2025年7月
# Smart Office Assistant AI

事務作業専用AIアシスタント - LINEボットによる包括的オフィス業務支援システム

## 📋 概要

このシステムは、企業の事務スタッフが日常業務で必要な情報を、LINEを通じて素早く検索・確認できる統合型AIアシスタントです。総務・人事から経理・営業事務まで、オフィス業務全般をカバーする包括的なソリューションを提供します。

### 🚀 主な機能

#### 📊 **事務業務効率化機能**
- **社内規定検索**: 就業規則、有給申請手順、経費精算方法の確認
- **手続きガイド**: 各種申請書の書き方、提出期限、承認フローの案内
- **業務プロセス最適化**: 作業手順の改善提案、効率化のアドバイス
- **文書テンプレート**: 契約書、提案書、報告書のひな形提供

#### 💼 **人事・総務支援**
- **労務管理**: 勤怠管理、休暇申請、残業申請の手続き案内
- **給与・福利厚生**: 給与明細の見方、各種手当、保険制度の説明
- **社員情報管理**: 組織図、部署情報、連絡先の確認
- **研修・教育**: 研修プログラム、スキルアップ支援、資格取得制度

#### 📈 **経理・会計サポート**
- **経費処理**: 経費精算、仕訳処理、税務処理の手順案内
- **予算管理**: 部署別予算、支出分析、コスト削減提案
- **請求・支払管理**: 請求書発行、支払スケジュール、債権管理
- **財務レポート**: 月次決算、損益分析、キャッシュフロー管理

#### 🔄 **営業・顧客管理**
- **顧客情報管理**: 顧客データベース、商談履歴、フォローアップ
- **営業支援**: 提案書作成、見積もり計算、契約書管理
- **売上分析**: 売上実績、目標達成率、市場動向分析
- **マーケティング**: キャンペーン管理、効果測定、顧客セグメント分析

#### 🤖 **AI高度機能**
- **スマートスケジューリング**: 会議室予約、スケジュール調整、リマインダー設定
- **自動文書生成**: 議事録、レポート、メール文面の自動作成
- **データ分析**: 業務データの可視化、トレンド分析、予測分析
- **タスク管理**: プロジェクト管理、進捗追跡、優先度設定

#### 🌐 **Web連携・検索**
- **最新情報検索**: 法改正情報、業界動向、競合他社情報
- **外部システム連携**: CRM、ERP、会計システムとの連携
- **クラウドサービス**: Google Workspace、Microsoft 365の活用支援
- **セキュリティ**: 情報漏洩防止、アクセス権限管理、監査ログ

#### 📋 **ワークフロー自動化**
- **承認フロー**: 申請書の自動ルーティング、承認状況の追跡
- **レポート生成**: 定期レポートの自動作成、配信スケジュール管理
- **アラート機能**: 期限通知、重要事項の自動通知
- **統合ダッシュボード**: 各種指標の一元表示、リアルタイム更新

## 🛠️ 技術スタック

- **Python 3.11**
- **FastAPI**: WebAPIフレームワーク
- **LangChain**: AI処理・RAG実装・エージェント機能
- **OpenAI API**: GPT-4モデル・埋め込みベクトル生成
- **FAISS**: ベクトルデータベース（業務・規定知識）
- **LINE Messaging API**: LINEボット機能
- **N8N**: ワークフロー自動化（オプション）
- **Serper API**: Web検索機能
- **Conda**: 環境管理

## 📦 環境構築手順

### 1. 事前準備

#### 必要なAPIキーの取得
1. **OpenAI API**
   - [OpenAI Platform](https://platform.openai.com/)でアカウント作成
   - APIキーを生成（GPT-4o-miniアクセス可能）
   - 課金設定を完了

2. **LINE Messaging API**
   - [LINE Developers](https://developers.line.biz/)でチャンネル作成
   - Channel Access TokenとChannel Secretを取得

3. **Serper API（オプション）**
   - [Serper](https://serper.dev/)でAPIキー取得（Web検索機能用）

### 2. プロジェクトのクローン・移動

```bash
# リポジトリのクローン
git clone https://github.com/HBM-system/ai-agent.git
cd ai-agent
```

### 3. Conda環境の構築

```bash
# 1. Conda環境の作成
conda create --name office-ai python=3.11 -y

# 2. 環境の有効化
conda activate office-ai
# ターミナルが (office-ai) から始まることを確認

# 3. FAISSのインストール
conda install -c pytorch faiss-cpu -y

# 4. その他ライブラリのインストール
pip install -r requirements.txt

# 5. OpenAI関連ライブラリの追加インストール（必要に応じて）
pip install openai langchain-openai tiktoken
```

### 4. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下を設定：

```env
# OpenAI API（必須）
OPENAI_API_KEY=sk-your_openai_api_key_here

# LINE Bot API（必須）
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# Web検索API（オプション）
SERPER_API_KEY=your_serper_api_key_here

# ワークフロー自動化（オプション）
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id

# その他（オプション）
GEMINI_API_KEY=your_gemini_api_key
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
✅ 事務規定データベースを 'faiss_index_office' フォルダに保存しました。
✅ 手続きガイドデータベースを 'faiss_index_procedures' フォルダに保存しました。
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
AIの知識データベースの準備が完了しました。
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
smart-office-ai/
├── README.md
├── requirements.txt
├── setup_vector_db.py          # データベース構築スクリプト
├── test_server.py              # 開発用テストサーバー
├── .env                        # 環境変数（要作成）
├── faiss_index_office/         # 事務規定データベース（自動生成）
├── faiss_index_procedures/     # 手続きガイドデータベース（自動生成）
└── src/
    ├── main.py                 # メインアプリケーション
    ├── config.py               # 設定管理
    ├── data/
    │   ├── office_docs/        # 事務規定文書（.md形式）
    │   │   ├── work_regulations.md
    │   │   ├── leave_policy.md
    │   │   ├── expense_policy.md
    │   │   └── welfare_benefits.md
    │   ├── procedures_docs/    # 手続きガイド文書（.md形式）
    │   │   ├── expense_procedures.md
    │   │   ├── leave_procedures.md
    │   │   └── meeting_room_booking.md
    │   └── dummy_data/         # デモ用データ
    │       ├── employees.json
    │       ├── departments.json
    │       ├── expense_records.json
    │       ├── attendance_records.json
    │       └── [その他データファイル]
    ├── services/               # 各種サービス
    │   ├── router.py           # 質問分類サービス
    │   ├── rag_service.py      # RAG検索サービス
    │   ├── agent_service.py    # AIエージェント
    │   ├── office_efficiency_service.py
    │   ├── hr_management_service.py
    │   ├── accounting_service.py
    │   ├── sales_support_service.py
    │   ├── schedule_service.py
    │   ├── document_service.py
    │   ├── web_search_service.py
    │   ├── conversation_manager.py
    │   └── n8n_connector.py    # N8N連携（オプション）
    ├── scripts/                # データ生成スクリプト
    │   ├── generate_dummy_data.py
    │   └── generate_office_data.py
    └── utils/                  # ユーティリティ
        └── report_parser.py    # レポート解析
```

## 🧪 動作確認・使用例

### 1. LINEボットのテスト

LINEで以下のメッセージを送信してテスト：

#### 📊 **事務業務関連**
- 「有給休暇の申請方法を教えて」
- 「経費精算の手順は？」
- 「会議室の予約方法は？」
- 「残業申請の期限はいつ？」

#### 💼 **人事・総務関連**
- 「健康保険の扶養家族追加手続きは？」
- 「退職時の手続きを教えて」
- 「社員研修の申し込み方法は？」
- 「住所変更届の提出先は？」

#### 📈 **経理・会計関連**
- 「交通費の上限金額は？」
- 「接待費の精算に必要な書類は？」
- 「予算申請のスケジュールは？」
- 「支払締切日を教えて」

#### 🔄 **営業・顧客管理**
- 「見積書のテンプレートはある？」
- 「契約書の印紙税はいくら？」
- 「顧客情報の更新方法は？」
- 「売上報告の締切は？」

#### 🤖 **AI高度機能**
- 「要約して」「まとめて」（前回の回答を簡潔に）
- 「最新の労働法改正情報を検索して」（Web検索）
- 複雑な事務手続き質問（エージェント機能による多段階処理）

### 2. 期待される動作

- **高速応答**: 質問送信後、数秒以内に適切な回答
- **自動分類**: 16カテゴリによる質問内容の自動判別
- **構造化レポート**: 分析結果の詳細で実用的なレポート生成
- **コンテキスト維持**: 会話履歴を活用した継続的な対話
- **多機能連携**: 検索・分析・外部API連携の組み合わせ

## 🎯 システムの特徴

### 🧠 **AI エージェント機能**
複数のツール（RAG検索、Web検索、データ分析）を組み合わせて複雑な質問に対応

### 📈 **高度な分析レポート**
- 業務効率分析：作業時間、生産性、改善提案
- 人事分析：勤怠状況、研修効果、人材評価
- 経理分析：経費動向、予算執行率、コスト最適化

### 🔄 **ワークフロー統合**
N8Nとの連携により、承認フロー、レポート出力、通知を自動化

### 💾 **包括的データベース**
- 社員情報・組織構成
- 業務手順・規定集
- 経費・勤怠データ
- 顧客・売上情報

## 🔧 トラブルシューティング

### よくあるエラーと解決方法

#### 1. `ModuleNotFoundError: No module named 'langchain_openai'`
```bash
pip install langchain-openai langchain-community
```

#### 2. `AttributeError: type object 'Config' has no attribute 'OPENAI_API_KEY'`
- `.env` ファイルにOPENAI_API_KEYが設定されているか確認
- APIキーが有効で課金設定が完了しているか確認

#### 3. ベクトルデータベースの構築エラー
```bash
# データベースを再構築
rm -rf faiss_index_*
python3 setup_vector_db.py
```

#### 4. 依存関係の競合エラー
```bash
# 環境を完全にリセット
conda deactivate
conda env remove --name office-ai
# 再度「3. Conda環境の構築」から実行
```

## 📊 システム性能

- **対応社員数**: 500名（EMP-2024-0001〜EMP-2024-0500）
- **知識ベース**: 事務・手続きガイド合計20+文書
- **分析カテゴリ**: 16種類の自動分類
- **応答時間**: 平均2-5秒
- **同時接続**: 複数ユーザー対応

## 🚀 今後の拡張予定

- ERPシステムとの連携
- 電子決裁システムとの統合
- 音声認識・音声応答機能
- モバイルアプリ版の開発
- 他社システムとの連携

## 📄 ライセンス

このプロジェクトは企業の事務業務効率化を目的として開発されています。
商用利用時は適切なライセンス確認を行ってください。

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. 全ての環境変数が正しく設定されているか
2. 必要なAPIキーが有効で、課金設定が完了しているか  
3. Conda環境が正しく有効化されているか（ターミナルに`(office-ai)`表示）
4. データベース構築が成功しているか（faiss_index_*フォルダの存在確認）
5. インターネット接続が正常か（Web検索・API通信用）

---

**開発環境**: macOS (Apple Silicon), Python 3.11, Conda  
**最終更新**: 2025年8月  
**バージョン**: 1.0 - 包括的オフィス業務支援システム
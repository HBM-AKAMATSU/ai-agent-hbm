# Smart Hospital AI Assistant

医療現場向けAIアシスタント - LINEボットによる包括的病院業務支援システム

## 📋 概要

このシステムは、病院職員が日常業務で必要な情報を、LINEを通じて素早く検索・確認できる統合型AIアシスタントです。診療支援から事務処理まで、病院業務全般をカバーする包括的なソリューションを提供します。

### 🚀 主な機能

#### 🏥 **診療支援機能**
- **医療情報検索**: 薬剤情報、用法用量、副作用、相互作用の確認
- **患者固有ダブルチェック**: A2024-XXXX形式患者IDによる個別薬剤安全確認
- **診療実績分析**: 当院の症例統計、治療成績、研究データ支援
- **臨床分析**: 疾患別分析、論文研究支援、エビデンス検索

#### 📊 **医療事務向け高度分析**
- **診療報酬分析**: 査定率、返戻分析、収益構造の詳細レポート
- **病床管理分析**: 稼働率、在院日数、退院調整の効率化提案
- **事務効率化分析**: スタッフ生産性、エラー率、業務改善提案
- **競合比較**: 地域医療機関との収益・実績比較

#### 📋 **事務情報検索**
- **院内規定検索**: 有給休暇、育児休業、通勤手当等の制度確認
- **職員研修分析**: 研修効果測定、個別職員の成長記録
- **スタッフ情報**: 部署目標、個人目標、研修履歴の照会

#### 🔄 **ワークフロー自動化**
- **シフト組み**: 希望日程からの自動シフト表生成（n8n連携）
- **レポート生成**: 構造化された業務レポートの自動作成
- **タスク管理**: n8nワークフローとの連携による業務自動化

#### 🤖 **AI高度機能**
- **エージェント**: 複数ツールを組み合わせた複雑な質問への対応
- **Web検索**: 最新医療情報の検索・要約
- **会話履歴**: コンテキストを維持した継続的な対話
- **自動分類**: 16カテゴリによる高精度な質問分類

## 🛠️ 技術スタック

- **Python 3.11**
- **FastAPI**: WebAPIフレームワーク
- **LangChain**: AI処理・RAG実装・エージェント機能
- **OpenAI API**: GPT-4モデル・埋め込みベクトル生成
- **FAISS**: ベクトルデータベース（医療・事務知識）
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
git clone https://github.com/HBM-SS/smart-hospital-ai.git
cd smart-hospital-ai
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
smart-hospital-ai/
├── README.md
├── requirements.txt
├── setup_vector_db.py          # データベース構築スクリプト
├── test_server.py              # 開発用テストサーバー
├── .env                        # 環境変数（要作成）
├── faiss_index_admin/          # 事務データベース（自動生成）
├── faiss_index_medical/        # 医療データベース（自動生成）
└── src/
    ├── main.py                 # メインアプリケーション
    ├── config.py               # 設定管理
    ├── data/
    │   ├── admin_docs/         # 事務規定文書（.md形式）
    │   │   ├── leave_policy.md
    │   │   ├── childcare_leave_policy.md
    │   │   ├── department_and_personal_goals.md
    │   │   └── commuting_allowance_policy.md
    │   ├── medical_docs/       # 医薬品・医療情報文書（.md形式）
    │   │   ├── fracture_outcomes_80plus.md
    │   │   └── stroke_diagnosis_ed.md
    │   └── dummy_data/         # デモ用データ
    │       ├── patients.json
    │       ├── detailed_patients.json
    │       ├── staff_training_records.json
    │       ├── billing_records.json
    │       └── [その他データファイル]
    ├── services/               # 各種サービス
    │   ├── router.py           # 質問分類サービス
    │   ├── rag_service.py      # RAG検索サービス
    │   ├── agent_service.py    # AIエージェント
    │   ├── double_check.py     # ダブルチェックサービス
    │   ├── enhanced_double_check.py
    │   ├── enhanced_clinical_analysis.py
    │   ├── billing_analysis_service.py
    │   ├── bed_management_service.py
    │   ├── admin_efficiency_service.py
    │   ├── staff_training_service.py
    │   ├── shift_scheduling_service.py
    │   ├── web_search_service.py
    │   ├── conversation_manager.py
    │   └── n8n_connector.py    # N8N連携（オプション）
    ├── scripts/                # データ生成スクリプト
    │   ├── generate_dummy_data.py
    │   └── generate_comprehensive_data.py
    └── utils/                  # ユーティリティ
        └── report_parser.py    # レポート解析
```

## 🧪 動作確認・使用例

### 1. LINEボットのテスト

LINEで以下のメッセージを送信してテスト：

#### 🏥 **診療支援関連**
- 「ワーファリンの初回投与量を教えて」
- 「患者A2024-0156にワーファリン処方予定、チェックお願いします」
- 「80歳以上の大腿骨骨折の治療成績は？」
- 「脳梗塞のt-PA投与例での転帰について、当院の実績は？」

#### 📊 **医療事務向け分析**
- 「査定率の分析をお願いします」
- 「今月の診療報酬収益分析を見せて」
- 「病床稼働率を改善したい」
- 「在院日数の分析をして」
- 「競合他院との比較はどうですか？」

#### 📋 **事務・人事関連**
- 「赤松の残りの有給休暇日数は？」
- 「育児休業の取得期間と手当について教えて」
- 「経理部の2025年度の部署目標は？」
- 「自転車通勤の申請方法と注意点は？」

#### 👥 **職員研修関連**
- 「佐藤さんが昨年取得した研修内容について教えて」
- 「研修効果の測定結果は？」
- 「職員教育の成果分析をお願いします」

#### 🔄 **ワークフロー自動化**
- 「シフト組んで：田中は1日休み、鈴木は夜勤希望、佐藤は日勤固定」
- 「来週のシフト表作成お願いします」

#### 🤖 **AI高度機能**
- 「要約して」「まとめて」（前回の回答を簡潔に）
- 「最新の心疾患治療ガイドラインを検索して」（Web検索）
- 複雑な医療事務質問（エージェント機能による多段階処理）

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
- 診療報酬分析：査定率、返戻分析、収益構造
- 病床管理：稼働率、在院日数、効率化提案
- 競合比較：地域医療機関との詳細比較

### 🔄 **ワークフロー統合**
N8Nとの連携により、シフト作成やレポート出力を自動化

### 💾 **包括的データベース**
- 500名の患者データ（A2024-XXXX形式）
- 職員研修記録・効果分析
- 診療実績・収益データ
- 院内規定・制度情報

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
conda env remove --name hospital-ai
# 再度「3. Conda環境の構築」から実行
```

#### 5. LangChainの警告メッセージ
```python
# 修正前
from langchain.vectorstores import FAISS
# 修正後
from langchain_community.vectorstores import FAISS
```

## 📊 システム性能

- **対応患者数**: 500名（A2024-0001〜A2024-0500）
- **知識ベース**: 医療・事務合計20+文書
- **分析カテゴリ**: 16種類の自動分類
- **応答時間**: 平均2-5秒
- **同時接続**: 複数ユーザー対応

## 🚀 今後の拡張予定

- 電子カルテシステム連携
- リアルタイム患者データ同期
- 音声認識・音声応答機能
- モバイルアプリ版の開発
- 他病院システムとの連携

## 📄 ライセンス

このプロジェクトは医療現場での業務効率化を目的として開発されています。
商用利用時は適切なライセンス確認を行ってください。

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. 全ての環境変数が正しく設定されているか
2. 必要なAPIキーが有効で、課金設定が完了しているか  
3. Conda環境が正しく有効化されているか（ターミナルに`(hospital-ai)`表示）
4. データベース構築が成功しているか（faiss_index_*フォルダの存在確認）
5. インターネット接続が正常か（Web検索・API通信用）

---

**開発環境**: macOS (Apple Silicon), Python 3.11, Conda  
**最終更新**: 2025年7月  
**バージョン**: 2.0 - 包括的病院業務支援システム
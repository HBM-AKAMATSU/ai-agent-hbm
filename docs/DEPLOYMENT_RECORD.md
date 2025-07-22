# Smart Hospital AI 実装記録

実装日時: $(date '+%Y年%m月%d日 %H:%M:%S')

## プロジェクト概要
- **プロジェクト名**: Smart Hospital AI Assistant
- **目的**: 医療現場向けLINEボット（事務・医療情報検索）
- **サーバー**: Xserver VPS
- **ドメイン**: https://create-mo.com
- **LINE Bot**: 正常動作中

## 技術スタック
- **言語**: Python 3.10
- **フレームワーク**: FastAPI
- **AI**: OpenAI GPT-4o-mini + RAG
- **ベクトルDB**: FAISS
- **Webサーバー**: Nginx
- **SSL**: Let's Encrypt
- **プロセス管理**: tmux/systemd

## システム構成
```
create-mo.com (HTTPS)
    ↓
Nginx (ポート443)
    ↓
Smart Hospital AI (ポート8000)
    ↓
OpenAI API + FAISS DB
```

## 主要機能
1. **自動質問分類**: admin/medical/double_check/task/unknown
2. **RAG検索**: 事務規定・医薬品情報データベース
3. **ダブルチェック**: 投薬前安全確認
4. **LINE連携**: リアルタイム回答

## データベース構成
- **事務データベース**: faiss_index_admin (経費精算等)
- **医療データベース**: faiss_index_medical (薬剤情報等)
- **患者データ**: ダミーデータでテスト済み

## セキュリティ設定
- SSL証明書: Let's Encrypt (自動更新)
- ファイアウォール: 22, 80, 443ポートのみ開放
- 環境変数: .env ファイルで管理（GitHubには非公開）

## 運用状況
- **アプリケーション**: 正常稼働中
- **HTTPS**: 正常アクセス可能
- **LINE Bot**: テスト完了・正常動作
- **監視**: tmuxセッションで24時間稼働

## テスト結果
✅ 医療情報検索: "ワーファリンについて教えて" → 詳細回答
✅ 事務情報検索: "学会参加費の精算方法" → 適切な案内
✅ HTTPS接続: create-mo.com → 正常
✅ SSL証明書: 有効期限まで3ヶ月

## トラブルシューティング記録
1. **DNS問題**: Xserverレンタルサーバー→VPS用ネームサーバーに変更で解決
2. **SSL設定**: 手動でNginx設定を作成してcertbot実行
3. **アプリ起動**: tmuxセッション利用でバックグラウンド実行

## 今後の改善点
- systemdサービス化（より安定した運用）
- モニタリング設定（Prometheus + Grafana）
- ログローテーション設定
- バックアップ自動化

## 緊急時の対応
- **アプリ再起動**: `tmux attach -t hospital-ai`
- **Nginx再起動**: `systemctl restart nginx`
- **SSL更新**: `certbot renew`
- **ログ確認**: `journalctl -u smart-hospital-ai`

---
記録者: Smart Hospital AI 開発チーム

## 実行時システム情報
- 実行日時: 2025年  7月 22日 火曜日 19:24:01 JST
- サーバー: x210-131-210-25
- OS: Ubuntu 22.04.5 LTS
- Python: Python 3.10.12

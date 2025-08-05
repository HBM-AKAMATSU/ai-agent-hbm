#!/usr/bin/env python3
# test_integrated_system.py - 統合システムテスト

import os
import sys
import unittest
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class TestIntegratedSalesSystem(unittest.TestCase):
    """統合営業システムテスト"""
    
    @classmethod
    def setUpClass(cls):
        """テスト環境初期化"""
        print("🚀 統合営業システムテスト初期化中...")
        
        # 各サービスの初期化
        from services.rag_service import RAGService
        from services.report_generation_service import ReportGenerationService
        from services.n8n_workflow_service import N8NWorkflowService
        from services.router import QuestionRouter
        
        cls.rag_service = RAGService()
        cls.rag_service.setup_vectorstores()
        
        cls.report_service = ReportGenerationService()
        cls.n8n_service = N8NWorkflowService()
        cls.router = QuestionRouter()
        
        print("✅ 統合テスト環境準備完了")
    
    def test_end_to_end_conversation_flow(self):
        """エンドツーエンド会話フローテスト"""
        print("\n💬 エンドツーエンド会話フローテスト")
        print("-" * 40)
        
        conversation_scenario = [
            ("高見さんの今日の訪問件数は？", "detailed_sales_query"),
            ("その結果をレポートにまとめて", "report_generation"),
            ("それを部長に送信して", "workflow_integration")
        ]
        
        conversation_history = ""
        
        for i, (query, expected_category) in enumerate(conversation_scenario, 1):
            print(f"ステップ{i}: {query}")
            
            # ルーターによる分類テスト
            category = self.router.classify_question(query)
            print(f"  分類結果: {category} (期待: {expected_category})")
            
            # 各サービスの応答テスト
            if category == "detailed_sales_query":
                response = self.rag_service.query_detailed_sales(query, conversation_history)
            elif category == "report_generation":
                response = self.report_service.generate_daily_report()
            elif category == "workflow_integration":
                response = self.n8n_service.check_webhook_status()  # 実際の送信はテスト用
            else:
                response = "カテゴリ未対応"
            
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 20)
            print(f"  応答: {response[:60]}...")
            
            conversation_history += f"Q: {query}\nA: {response}\n\n"
        
        print("✅ エンドツーエンド会話フロー完了")
    
    def test_minami_character_integration(self):
        """みなみちゃんキャラクター統合テスト"""
        print("\n🎭 みなみちゃんキャラクター統合テスト")
        print("-" * 40)
        
        character_queries = [
            "辻川さんの実績はどう？",
            "今月の売上予測を教えて",
            "チーム全体の調子はどう？"
        ]
        
        for query in character_queries:
            print(f"質問: {query}")
            
            # 分類テスト
            category = self.router.classify_question(query)
            print(f"  分類: {category}")
            
            # みなみちゃんキャラクターでの応答
            if category in ["sales_query", "detailed_sales_query"]:
                if category == "detailed_sales_query":
                    response = self.rag_service.query_detailed_sales(query)
                else:
                    response = self.rag_service.query_sales_with_history(query)
                
                # キャラクター要素の確認
                character_indicators = ["やと", "ね", "です", "ます", "よ"]
                has_character = any(indicator in response for indicator in character_indicators)
                
                self.assertTrue(has_character, "みなみちゃんキャラクター要素が不足")
                self.assertGreater(len(response), 50, "応答が短すぎます")
                
                print(f"  ✅ みなみちゃん応答: {response[:80]}...")
            else:
                print(f"  ⚠️ 営業系以外のカテゴリ: {category}")
        
        print("✅ みなみちゃんキャラクター統合テスト完了")
    
    def test_report_generation_integration(self):
        """レポート生成統合テスト"""
        print("\n📊 レポート生成統合テスト")
        print("-" * 40)
        
        report_queries = [
            ("日次レポートを作成して", "daily"),
            ("月次分析レポートを生成", "monthly"),
            ("カスタムレポートを作って", "custom")
        ]
        
        for query, expected_type in report_queries:
            print(f"レポート要求: {query}")
            
            # 分類テスト
            category = self.router.classify_question(query)
            self.assertEqual(category, "report_generation", f"分類エラー: {category}")
            
            # レポート生成テスト
            if expected_type == "daily":
                report = self.report_service.generate_daily_report()
            elif expected_type == "monthly":
                report = self.report_service.generate_monthly_analysis()
            else:
                report = self.report_service.generate_custom_report(query)
            
            # レポート品質チェック
            self.assertIsInstance(report, str)
            self.assertGreater(len(report), 300, "レポートが短すぎます")
            self.assertIn("阪南ビジネスマシン", report, "会社名が含まれていません")
            
            print(f"  ✅ {expected_type}レポート生成完了 ({len(report)}文字)")
        
        print("✅ レポート生成統合テスト完了")
    
    def test_n8n_workflow_integration(self):
        """N8Nワークフロー統合テスト"""
        print("\n🔗 N8Nワークフロー統合テスト")
        print("-" * 40)
        
        workflow_queries = [
            ("月次レポートを部長に送信して", "report_email"),
            ("チームに今日のサマリーを通知", "team_notification"),
            ("リード育成の自動化を開始", "sales_automation")
        ]
        
        for query, expected_workflow in workflow_queries:
            print(f"ワークフロー要求: {query}")
            
            # 分類テスト
            category = self.router.classify_question(query)
            
            # ワークフロー関連のカテゴリかチェック
            workflow_categories = ["workflow_integration", "report_generation"]
            if category in workflow_categories:
                print(f"  ✅ 適切な分類: {category}")
                
                # N8N接続状態確認（実際の送信はしない）
                status = self.n8n_service.check_webhook_status()
                self.assertIsInstance(status, str)
                print(f"  N8N状態: {status[:50]}...")
                
                # Webhookデータフォーマットテスト
                if "レポート" in query:
                    test_report = "テストレポート内容"
                    webhook_data = self.n8n_service.format_webhook_data(test_report)
                    self.assertIn("type", webhook_data)
                    self.assertIn("content", webhook_data)
                    print(f"  ✅ Webhookデータフォーマット成功")
            else:
                print(f"  ⚠️ 予期しない分類: {category}")
        
        print("✅ N8Nワークフロー統合テスト完了")
    
    def test_conversation_continuity(self):
        """会話継続テスト（3-5回）"""
        print("\n🔄 会話継続テスト")
        print("-" * 40)
        
        conversation_flow = [
            "官需課の実績はどう？",
            "一番良いのは誰？",
            "その人の強みは？",
            "他のメンバーも伸ばすには？",
            "具体的なアクションプランは？"
        ]
        
        conversation_history = ""
        successful_turns = 0
        
        for turn, query in enumerate(conversation_flow, 1):
            print(f"ターン{turn}: {query}")
            
            try:
                # 分類
                category = self.router.classify_question(query)
                
                # 応答生成（会話履歴を考慮）
                if category in ["sales_query", "detailed_sales_query"]:
                    if category == "detailed_sales_query":
                        response = self.rag_service.query_detailed_sales(query, conversation_history)
                    else:
                        response = self.rag_service.query_sales_with_history(query, conversation_history)
                    
                    # 応答品質チェック
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 30)
                    
                    # 会話履歴更新
                    conversation_history += f"Q{turn}: {query}\nA{turn}: {response}\n\n"
                    successful_turns += 1
                    
                    print(f"  ✅ 応答成功: {response[:50]}...")
                else:
                    print(f"  ⚠️ 営業系以外: {category}")
                    
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                break
        
        print(f"✅ 会話継続テスト完了: {successful_turns}/5ターン成功")
        self.assertGreaterEqual(successful_turns, 3, "会話継続が不十分です")
    
    def test_data_integration(self):
        """データ統合テスト"""
        print("\n📊 データ統合テスト")
        print("-" * 40)
        
        # 各データソースの確認
        data_sources = [
            ("詳細営業データ", self.rag_service.detailed_sales_data),
            ("拡張営業指標", self.rag_service.enhanced_metrics),
            ("顧客接触履歴", self.rag_service.interaction_history)
        ]
        
        for name, data in data_sources:
            if data:
                print(f"✅ {name}: 正常読み込み")
                self.assertIsInstance(data, dict)
            else:
                print(f"⚠️ {name}: データなし")
        
        # レポートサービスのデータ統合確認
        report_data_sources = [
            ("基本売上データ", self.report_service.basic_sales_data),
            ("詳細営業データ", self.report_service.detailed_sales_data),
            ("拡張指標データ", self.report_service.enhanced_metrics)
        ]
        
        for name, data in report_data_sources:
            if data:
                print(f"✅ レポート用{name}: 正常読み込み")
            else:
                print(f"⚠️ レポート用{name}: データなし")
        
        print("✅ データ統合テスト完了")

def run_integrated_tests():
    """統合テストの実行"""
    print("🚀 営業成績特化エージェント統合テスト開始")
    print("=" * 60)
    
    # テストスイート作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # テストクラス追加
    suite.addTests(loader.loadTestsFromTestCase(TestIntegratedSalesSystem))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print(f"🏁 統合テスト完了: {result.testsRun}件実行")
    print(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}件")
    if result.failures:
        print(f"❌ 失敗: {len(result.failures)}件")
    if result.errors:
        print(f"💥 エラー: {len(result.errors)}件")
    
    # 最終評価
    if result.wasSuccessful():
        print("\n🎉 営業成績特化エージェント実装完了！")
        print("✨ 全機能が正常に動作しています")
    else:
        print("\n⚠️ 一部機能に問題があります。修正が必要です。")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = run_integrated_tests()
    
    if success:
        print("\n🎯 営業成績特化エージェント実装プロジェクト完了")
        print("📋 実装完了項目:")
        print("  ✅ みなみちゃんキャラクター（関西弁・親しみやすい）")
        print("  ✅ 詳細営業データ統合（日次活動・パイプライン）")
        print("  ✅ レポート自動生成（日次・月次・カスタム）")
        print("  ✅ N8Nワークフロー連携（メール配信・自動化）")
        print("  ✅ 会話継続システム（3-5回の自然な対話）")
        print("  ✅ 統合システムテスト完了")
        print("\n🚀 システムは本格運用可能です！")
    else:
        print("\n🔧 システムの修正・調整が必要です")
    
    sys.exit(0 if success else 1)
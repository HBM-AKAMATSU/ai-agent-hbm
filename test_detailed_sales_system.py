#!/usr/bin/env python3
# test_detailed_sales_system.py - 詳細営業システムのテスト（TDD方式）

import os
import sys
import unittest
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.rag_service import RAGService
from services.agent_service import OfficeAIAgent

class TestDetailedSalesSystem(unittest.TestCase):
    """詳細営業システムのテストスイート"""
    
    @classmethod
    def setUpClass(cls):
        """テスト開始前の初期化"""
        print("🧪 詳細営業システムのテストを初期化中...")
        cls.rag_service = RAGService()
        cls.rag_service.setup_vectorstores()
        cls.agent = OfficeAIAgent(cls.rag_service)
        print("✅ テスト環境の初期化完了")
    
    def test_detailed_daily_activity_query(self):
        """詳細な日次活動データ取得テスト"""
        print("\n📊 詳細日次活動データ取得テスト中...")
        
        test_queries = [
            "高見さんの今日の訪問件数は？",
            "辻川さんの今週の電話件数を教えて",
            "小濱さんの商談進捗はどう？"
        ]
        
        for query in test_queries:
            print(f"  テスト質問: {query}")
            response = self.agent.process_query(query)
            
            # 応答内容の基本検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 50)  # 適切な長さの応答
            print(f"  ✅ 応答長: {len(response)}文字")
    
    def test_minami_character_response(self):
        """みなみちゃんキャラクター応答テスト"""
        print("\n🎭 みなみちゃんキャラクター応答テスト中...")
        
        query = "官需課の実績はどう？"
        response = self.agent.process_query(query)
        
        # キャラクター要素の検証（実装後に詳細化）
        character_elements = [
            # 現時点では基本的な応答性のみ検証
            # 実装後に関西弁、親しみやすさなどを追加
        ]
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 30)
        print(f"  ✅ みなみちゃん応答: {response[:100]}...")
    
    def test_conversation_continuity(self):
        """会話継続システムテスト（3-5回）"""
        print("\n💬 会話継続システムテスト中...")
        
        conversation_flow = [
            "高見さんの売上実績は？",
            "2位は誰ですか？", 
            "その理由は何だと思う？",
            "改善提案はある？"
        ]
        
        responses = []
        for i, query in enumerate(conversation_flow):
            print(f"  会話ターン{i+1}: {query}")
            response = self.agent.process_query(query)
            responses.append(response)
            
            # 各応答の基本検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 20)
            print(f"    応答: {response[:80]}...")
        
        # 全体で3回以上の会話が成立
        self.assertGreaterEqual(len(responses), 3)
        print(f"  ✅ {len(responses)}回の会話継続成功")
    
    def test_sales_data_accuracy(self):
        """営業データ精度テスト"""
        print("\n📈 営業データ精度テスト中...")
        
        # 既知の阪南ビジネスマシンデータに基づくテスト
        accuracy_queries = [
            "辻川さんの4月の実績は？",  # 2,712万円のはず
            "官需課の4月の達成率は？",  # 105.3%のはず
            "RISO製品の販売状況は？"    # 主力商品のはず
        ]
        
        for query in accuracy_queries:
            print(f"  データ精度確認: {query}")
            response = self.agent.process_query(query)
            
            # データが含まれているかの基本検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 30)
            
            # 具体的な数値や情報が含まれているか（実装後詳細化）
            has_data = any(char.isdigit() for char in response)
            self.assertTrue(has_data, "応答に数値データが含まれていません")
            print(f"    ✅ データ含有確認済み")
    
    def test_question_understanding(self):
        """質問理解・分類テスト"""
        print("\n🤔 質問理解・分類テスト中...")
        
        understanding_queries = [
            ("営業成績を教えて", "sales_query"),
            ("レポートを送信して", "report_generation"),  # 今後実装予定
            ("詳細な訪問データは？", "detailed_sales_query")  # 今回新規
        ]
        
        for query, expected_category in understanding_queries:
            print(f"  理解テスト: {query} -> 期待カテゴリ: {expected_category}")
            response = self.agent.process_query(query)
            
            # 現時点では基本的な応答のみ検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 10)
            print(f"    ✅ 応答生成成功")

    def test_error_handling(self):
        """エラーハンドリング・フォールバックテスト"""
        print("\n⚠️ エラーハンドリングテスト中...")
        
        edge_cases = [
            "",  # 空の質問
            "存在しない担当者の実績は？",
            "あいうえお",  # 意味不明な質問
            "1234567890"   # 数字のみ
        ]
        
        for query in edge_cases:
            print(f"  エッジケーステスト: '{query}'")
            try:
                response = self.agent.process_query(query)
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 10)  # 何らかの応答があること
                print(f"    ✅ 適切にハンドリング済み")
            except Exception as e:
                self.fail(f"エッジケース '{query}' でエラー: {e}")

class TestMinamiCharacterSpecific(unittest.TestCase):
    """みなみちゃんキャラクター特化テスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.rag_service = RAGService()
        self.rag_service.setup_vectorstores()
        self.agent = OfficeAIAgent(self.rag_service)
    
    def test_friendly_tone(self):
        """親しみやすい口調テスト（実装後詳細化予定）"""
        print("\n😊 親しみやすい口調テスト中...")
        
        query = "営業成績はどう？"
        response = self.agent.process_query(query)
        
        # 現時点では基本応答のみ検証（実装後に詳細化）
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 20)
        print(f"  ✅ 基本応答確認: {response[:60]}...")
    
    def test_encouragement_and_support(self):
        """励まし・サポート機能テスト（実装後詳細化予定）"""
        print("\n💪 励まし・サポート機能テスト中...")
        
        queries = [
            "売上が下がって心配です",
            "今月の成績が良くない",
            "目標達成できるか不安"
        ]
        
        for query in queries:
            print(f"  サポートテスト: {query}")
            response = self.agent.process_query(query)
            
            # 基本的な応答生成確認
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 30)
            print(f"    ✅ サポート応答生成済み")

def run_sales_system_tests():
    """営業システムテストの実行"""
    print("🚀 詳細営業システム TDDテスト開始")
    print("=" * 60)
    
    # テストスイートの作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # テストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestDetailedSalesSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestMinamiCharacterSpecific))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print(f"🏁 テスト完了: {result.testsRun}件実行")
    print(f"✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}件")
    if result.failures:
        print(f"❌ 失敗: {len(result.failures)}件")
    if result.errors:
        print(f"💥 エラー: {len(result.errors)}件")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = run_sales_system_tests()
    
    if success:
        print("\n🎉 全テストが正常に完了しました！")
        print("次のステップ: 詳細営業データファイルの作成を開始してください。")
    else:
        print("\n⚠️ 一部のテストが失敗しました。実装を確認してください。")
    
    sys.exit(0 if success else 1)
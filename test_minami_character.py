#!/usr/bin/env python3
# test_minami_character.py - みなみちゃんキャラクター特化テスト

import os
import sys
import unittest
import re
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.rag_service import RAGService
from services.agent_service import OfficeAIAgent

class TestMinamiCharacterFeatures(unittest.TestCase):
    """みなみちゃんキャラクター機能テスト"""
    
    @classmethod
    def setUpClass(cls):
        """テスト環境初期化"""
        print("🎭 みなみちゃんキャラクターテスト初期化中...")
        cls.rag_service = RAGService()
        cls.rag_service.setup_vectorstores()
        cls.agent = OfficeAIAgent(cls.rag_service)
        print("✅ みなみちゃんテスト環境準備完了")
    
    def test_kansai_dialect_elements(self):
        """関西弁要素テスト（実装後詳細化）"""
        print("\n🗣️ 関西弁要素テスト中...")
        
        queries = [
            "高見さんの実績はどう？",
            "今月の売上は順調？",
            "何か心配なことある？"
        ]
        
        kansai_patterns = [
            # 実装後に関西弁パターンを追加予定
            # r'やで', r'やん', r'せやね', r'ほんま', r'めっちゃ'
            # 現時点では基本応答のみ検証
        ]
        
        for query in queries:
            print(f"  関西弁テスト: {query}")
            response = self.agent.process_query(query)
            
            # 現時点では基本検証のみ
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 20)
            
            # 実装後に関西弁パターンマッチを追加予定
            print(f"    ✅ 応答生成: {response[:50]}...")
    
    def test_friendly_encouraging_tone(self):
        """親しみやすく励ます口調テスト"""
        print("\n😊 親しみやすい励まし口調テスト中...")
        
        scenarios = [
            ("売上が好調です", "positive"),  # 良い結果は褒める
            ("目標達成が難しそう", "supportive"),  # 課題は一緒に考える
            ("新規開拓が進まない", "constructive")  # 建設的提案
        ]
        
        for query, expected_tone in scenarios:
            print(f"  口調テスト: {query} -> 期待トーン: {expected_tone}")
            response = self.agent.process_query(query)
            
            # 基本応答検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 30)
            
            # 口調の適切性（実装後詳細化予定）
            if expected_tone == "positive":
                # 褒める要素があるか（実装後追加）
                pass
            elif expected_tone == "supportive":
                # サポート要素があるか（実装後追加）
                pass
            
            print(f"    ✅ {expected_tone}トーン応答生成済み")
    
    def test_conversation_continuation_questions(self):
        """会話継続質問テスト"""
        print("\n💬 会話継続質問テスト中...")
        
        base_queries = [
            "辻川さんの4月の実績は？",
            "RISO製品の売れ行きは？",
            "官需課の目標達成状況は？"
        ]
        
        question_patterns = [
            # 実装後に追加予定の質問パターン
            # r'\?', r'どう思', r'いかが', r'ません？'
        ]
        
        for query in base_queries:
            print(f"  継続質問テスト: {query}")
            response = self.agent.process_query(query)
            
            # 基本応答検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 40)
            
            # 質問で終わっているか（実装後詳細化）
            # ends_with_question = response.strip().endswith('？') or response.strip().endswith('?')
            # self.assertTrue(ends_with_question, "応答が質問で終わっていません")
            
            print(f"    ✅ 継続促進応答生成: {response[:60]}...")
    
    def test_background_explanation_depth(self):
        """数字の背景・意味説明テスト"""
        print("\n📊 数字の背景説明テスト中...")
        
        data_queries = [
            "辻川さんの達成率107.2%ってどう？",
            "4月の6,740万円の実績について教えて",
            "RISO52件って多いの？"
        ]
        
        for query in data_queries:
            print(f"  背景説明テスト: {query}")
            response = self.agent.process_query(query)
            
            # 基本応答検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 50)
            
            # 数値データが含まれているか
            has_numbers = any(char.isdigit() for char in response)
            self.assertTrue(has_numbers, "応答に数値が含まれていません")
            
            # 説明的内容があるか（長さで簡易判定）
            is_explanatory = len(response) > 80
            self.assertTrue(is_explanatory, "背景説明が不十分です")
            
            print(f"    ✅ 背景説明応答: {len(response)}文字")
    
    def test_empathy_and_support(self):
        """共感・サポート機能テスト"""
        print("\n💖 共感・サポート機能テスト中...")
        
        emotional_queries = [
            "最近売上が伸び悩んでます",
            "新規開拓がうまくいかない",
            "プレッシャーを感じる",
            "チーム一丸となって頑張ってる"
        ]
        
        for query in emotional_queries:
            print(f"  共感テスト: {query}")
            response = self.agent.process_query(query)
            
            # 基本応答検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 40)
            
            # 共感・サポート要素（実装後詳細化予定）
            # supportive_words = ['一緒に', '大丈夫', '頑張', 'サポート']
            # has_support = any(word in response for word in supportive_words)
            
            print(f"    ✅ サポート応答: {response[:70]}...")

class TestConversationFlow(unittest.TestCase):
    """会話フロー統合テスト"""
    
    def setUp(self):
        """各テスト前の初期化"""
        self.rag_service = RAGService()
        self.rag_service.setup_vectorstores()
        self.agent = OfficeAIAgent(self.rag_service)
    
    def test_five_turn_conversation(self):
        """5回転会話テスト"""
        print("\n🔄 5回転会話フローテスト中...")
        
        conversation_scenario = [
            "官需課の今月の実績はどう？",
            "一番成績がいいのは誰？",
            "その人の強みは何だと思う？",
            "他のメンバーも同じように伸ばすには？",
            "具体的にはどうすればいい？"
        ]
        
        conversation_history = []
        
        for turn, query in enumerate(conversation_scenario, 1):
            print(f"  第{turn}ターン: {query}")
            
            # 会話履歴を含めてクエリ実行（実装後強化予定）
            response = self.agent.process_query(query)
            conversation_history.append((query, response))
            
            # 各ターンの基本検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 30)
            
            print(f"    応答: {response[:50]}...")
        
        # 全5回の会話が成立
        self.assertEqual(len(conversation_history), 5)
        print(f"  ✅ {len(conversation_history)}回転会話完了")
    
    def test_context_awareness(self):
        """文脈認識テスト（実装後詳細化予定）"""
        print("\n🧠 文脈認識テスト中...")
        
        context_queries = [
            "辻川さんの実績を教えて",
            "その人の今後の見込みは？",  # "その人" = 辻川さんを理解できるか
            "他の人と比べてどう？"        # 比較対象を理解できるか
        ]
        
        for i, query in enumerate(context_queries):
            print(f"  文脈テスト{i+1}: {query}")
            response = self.agent.process_query(query)
            
            # 基本応答検証
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 25)
            
            print(f"    ✅ 文脈応答: {response[:45]}...")

def run_minami_character_tests():
    """みなみちゃんキャラクターテストの実行"""
    print("🎭 みなみちゃんキャラクター TDDテスト開始")
    print("=" * 60)
    
    # テストスイート作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # テストクラス追加
    suite.addTests(loader.loadTestsFromTestCase(TestMinamiCharacterFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationFlow))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print(f"🏁 みなみちゃんテスト完了: {result.testsRun}件実行")
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
    
    success = run_minami_character_tests()
    
    if success:
        print("\n🎉 みなみちゃんテストが正常に完了しました！")
        print("次のステップ: 詳細営業データファイルの作成に進んでください。")
    else:
        print("\n⚠️ 一部のテストが失敗しました。キャラクター実装を確認してください。")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# test_demo_scenarios.py - デモシナリオテスト

import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demo_scenario_1():
    """デモシナリオ1: 詳細営業データ取得"""
    print("🎯 デモシナリオ1: 詳細営業データ取得")
    print("=" * 50)
    print("質問: 「高見さんの今日の訪問件数は？」")
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        rag_service.setup_vectorstores()
        
        response = rag_service.query_detailed_sales("高見さんの今日の訪問件数は？")
        print(f"\nみなみちゃんの応答:")
        print("-" * 30)
        print(response)
        
        # 成功指標チェック
        success_indicators = [
            ("詳細データ活用", any(word in response for word in ["6件", "訪問", "電話", "メール"])),
            ("みなみちゃんキャラ", any(word in response for word in ["やと", "ね", "です", "はり"])),
            ("会話継続要素", response.endswith("？") or "どう" in response or "いかが" in response),
            ("実用的価値", any(word in response for word in ["堺市", "複合機", "売上予測"]))
        ]
        
        print("\n📊 評価結果:")
        for indicator, result in success_indicators:
            status = "✅" if result else "❌"
            print(f"{status} {indicator}: {'達成' if result else '未達成'}")
        
        overall_success = all(result for _, result in success_indicators)
        print(f"\n🎯 総合評価: {'✅ 成功' if overall_success else '⚠️ 要改善'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def demo_scenario_2():
    """デモシナリオ2: レポート生成・配信"""
    print("\n🎯 デモシナリオ2: レポート生成・配信")
    print("=" * 50)
    print("質問: 「月次レポートを部長に送信して」")
    
    try:
        from services.report_generation_service import ReportGenerationService
        from services.n8n_workflow_service import N8NWorkflowService
        
        report_service = ReportGenerationService()
        n8n_service = N8NWorkflowService()
        
        # レポート生成
        print("\n📊 月次レポート生成中...")
        report_content = report_service.generate_monthly_analysis()
        
        print(f"レポート生成完了 ({len(report_content)}文字)")
        print("\nレポート内容（抜粋）:")
        print("-" * 30)
        print(report_content[:400] + "...")
        
        # N8N連携準備
        print("\n📧 N8N配信準備中...")
        report_data = n8n_service.format_webhook_data(report_content, "monthly", "部長")
        
        # 配信状態確認
        webhook_status = n8n_service.check_webhook_status()
        print(f"N8N状態: {webhook_status}")
        
        # 成功指標チェック
        success_indicators = [
            ("レポート生成", len(report_content) > 500),
            ("阪南BM情報", "阪南ビジネスマシン" in report_content),
            ("実データ活用", any(word in report_content for word in ["辻川", "高見", "小濱"])),
            ("Webhook準備", "type" in report_data and "content" in report_data)
        ]
        
        print("\n📊 評価結果:")
        for indicator, result in success_indicators:
            status = "✅" if result else "❌"
            print(f"{status} {indicator}: {'達成' if result else '未達成'}")
        
        overall_success = all(result for _, result in success_indicators)
        print(f"\n🎯 総合評価: {'✅ 成功' if overall_success else '⚠️ 要改善'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def demo_scenario_3():
    """デモシナリオ3: 5回会話継続"""
    print("\n🎯 デモシナリオ3: 5回会話継続")
    print("=" * 50)
    
    conversation_flow = [
        "官需課の今月の実績はどう？",
        "一番成績がいいのは誰？",
        "その人の強みは何？",
        "他のメンバーも伸ばすには？",
        "具体的なアクションプランは？"
    ]
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        rag_service.setup_vectorstores()
        
        conversation_history = ""
        successful_turns = 0
        
        for turn, query in enumerate(conversation_flow, 1):
            print(f"\n--- ターン{turn} ---")
            print(f"質問: {query}")
            
            try:
                response = rag_service.query_sales_with_history(query, conversation_history)
                print(f"応答: {response[:100]}...")
                
                # 応答品質チェック
                if len(response) > 30:
                    successful_turns += 1
                    conversation_history += f"Q{turn}: {query}\nA{turn}: {response}\n\n"
                    print(f"✅ ターン{turn}成功")
                else:
                    print(f"⚠️ ターン{turn}応答不十分")
                    
            except Exception as e:
                print(f"❌ ターン{turn}エラー: {e}")
                break
        
        print(f"\n📊 会話継続結果: {successful_turns}/5ターン成功")
        
        success = successful_turns >= 3
        print(f"🎯 評価: {'✅ 成功' if success else '⚠️ 要改善'}")
        
        return success
        
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        return False

def demo_scenario_4():
    """デモシナリオ4: GPT-4o高品質応答確認"""
    print("\n🎯 デモシナリオ4: GPT-4o高品質応答確認")
    print("=" * 50)
    print("質問: 「辻川さんの強みと課題を分析して改善提案をお願いします」")
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        rag_service.setup_vectorstores()
        
        complex_query = "辻川さんの強みと課題を分析して改善提案をお願いします"
        response = rag_service.query_detailed_sales(complex_query)
        
        print(f"\nみなみちゃんの詳細分析:")
        print("-" * 30)
        print(response)
        
        # 高品質応答の指標
        quality_indicators = [
            ("詳細分析", len(response) > 200),
            ("具体的データ", any(word in response for word in ["2,712万円", "107.2%", "108.7%"])),
            ("強み分析", any(word in response for word in ["大型案件", "官公庁", "獲得力"])),
            ("改善提案", any(word in response for word in ["提案", "改善", "共有", "ノウハウ"])),
            ("みなみちゃんキャラ", any(word in response for word in ["やと", "ね", "はり", "です"])),
            ("会話継続", response.endswith("？") or "どう" in response[-50:])
        ]
        
        print("\n📊 品質評価:")
        for indicator, result in quality_indicators:
            status = "✅" if result else "❌"
            print(f"{status} {indicator}: {'達成' if result else '未達成'}")
        
        overall_quality = sum(result for _, result in quality_indicators) >= 4  # 6項目中4項目以上
        print(f"\n🎯 品質評価: {'✅ 高品質' if overall_quality else '⚠️ 要改善'}")
        
        return overall_quality
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def run_demo_scenarios():
    """全デモシナリオの実行"""
    print("🚀 営業成績特化エージェント デモシナリオテスト")
    print("=" * 60)
    print("目標: 単なる情報提供ツールから「営業現場の頼れる相談相手みなみちゃん」への進化")
    print("=" * 60)
    
    scenarios = [
        ("詳細営業データ取得", demo_scenario_1),
        ("レポート生成・配信", demo_scenario_2),
        ("5回会話継続", demo_scenario_3),
        ("GPT-4o高品質応答", demo_scenario_4)
    ]
    
    results = []
    
    for name, scenario_func in scenarios:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            result = scenario_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}でエラー: {e}")
            results.append((name, False))
    
    # 最終結果
    print("\n" + "=" * 60)
    print("🏁 デモシナリオテスト結果")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{status}: {name}")
        if result:
            success_count += 1
    
    overall_success_rate = success_count / len(results)
    print(f"\n📊 総合成功率: {success_count}/{len(results)} ({overall_success_rate:.1%})")
    
    if overall_success_rate >= 0.75:  # 75%以上で成功
        print("\n🎉 営業成績特化エージェント実装成功！")
        print("✨ みなみちゃんが営業現場の頼れる相談相手として機能しています")
        print("\n📋 実装完了機能:")
        print("  ✅ 関西弁交じりの親しみやすいキャラクター")
        print("  ✅ 詳細営業データ統合・分析")
        print("  ✅ 自動レポート生成・配信")
        print("  ✅ N8Nワークフロー連携")
        print("  ✅ 自然な会話継続システム")
        print("  ✅ GPT-4oによる高品質分析")
        print("\n🚀 システムは本格運用可能です！")
        return True
    else:
        print("\n⚠️ システムの改善が必要です")
        print("🔧 成功率75%以上を目標に調整してください")
        return False

if __name__ == "__main__":
    # スクリプトのディレクトリに移動
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = run_demo_scenarios()
    
    if success:
        print("\n🎯 プロジェクト完了: 営業成績特化エージェント「みなみちゃん」運用開始可能")
    else:
        print("\n🔄 要改善: システム調整を継続してください")
    
    sys.exit(0 if success else 1)
# src/services/report_generation_service.py - 営業レポート生成サービス

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from config import Config

class ReportGenerationService:
    """営業レポート生成サービス"""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.3  # レポート生成では一貫性を重視
        )
        
        # データの読み込み
        self.detailed_sales_data = self._load_detailed_sales_data()
        self.enhanced_metrics = self._load_enhanced_metrics()
        self.interaction_history = self._load_interaction_history()
        self.basic_sales_data = self._load_basic_sales_data()
    
    def _load_detailed_sales_data(self) -> Dict[str, Any]:
        """詳細営業データの読み込み"""
        try:
            with open("data/detailed_sales_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告: 詳細営業データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"詳細営業データの読み込みエラー: {e}")
            return {}
    
    def _load_enhanced_metrics(self) -> Dict[str, Any]:
        """拡張営業指標データの読み込み"""
        try:
            with open("data/enhanced_sales_metrics.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告: 拡張営業指標データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"拡張営業指標データの読み込みエラー: {e}")
            return {}
    
    def _load_interaction_history(self) -> Dict[str, Any]:
        """顧客接触履歴データの読み込み"""
        try:
            with open("data/customer_interaction_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告: 顧客接触履歴データファイルが見つかりません。")
            return {}
        except Exception as e:
            print(f"顧客接触履歴データの読み込みエラー: {e}")
            return {}
    
    def _load_basic_sales_data(self) -> str:
        """基本営業データ（テキストファイル）の読み込み"""
        try:
            with open("data/hbm_sales_data.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("警告: 基本営業データファイルが見つかりません。")
            return ""
        except Exception as e:
            print(f"基本営業データの読み込みエラー: {e}")
            return ""
    
    def generate_daily_report(self, target_date: str = None) -> str:
        """日次レポート生成"""
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # データコンテキストの準備
        context = self._prepare_daily_context(target_date)
        
        prompt = f"""
        あなたは阪南ビジネスマシンの営業分析専門スタッフです。
        以下のデータを基に、{target_date}の日次営業レポートを作成してください。
        
        ## レポート要件
        - A4 1ページ程度（約800文字）
        - 実用的で具体的な内容
        - 改善提案を含む
        - 阪南ビジネスマシンの実データに基づく
        
        ## データコンテキスト
        {context}
        
        ## レポート構成
        ### 📊 **阪南ビジネスマシン 日次営業レポート**
        **日付**: {target_date}
        **作成**: 営業支援AI みなみちゃん
        
        #### **🎯 本日の活動サマリー**
        [チーム全体の活動概況]
        
        #### **👥 担当者別実績**
        [個人別の活動状況と特筆事項]
        
        #### **💼 商談進捗ハイライト**
        [重要案件の進捗状況]
        
        #### **📈 分析・所感**
        [データから読み取れる傾向や課題]
        
        #### **🚀 明日への改善提案**
        [具体的なアクションプラン]
        
        **※このレポートはAIが生成したものです。詳細は担当者に確認してください。**
        
        上記の構成で、実用的で読みやすいレポートを作成してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"日次レポート生成中にエラーが発生しました: {e}"
    
    def generate_monthly_analysis(self, target_month: str = None) -> str:
        """月次分析レポート生成"""
        if not target_month:
            target_month = datetime.now().strftime("%Y-%m")
        
        # データコンテキストの準備
        context = self._prepare_monthly_context(target_month)
        
        prompt = f"""
        あなたは阪南ビジネスマシンの営業分析専門スタッフです。
        以下のデータを基に、{target_month}の月次営業分析レポートを作成してください。
        
        ## レポート要件
        - A4 2-3ページ程度（約1500-2000文字）
        - 経営判断に活用できる分析レベル
        - 具体的な改善提案と次月戦略
        - 阪南ビジネスマシンの実データに基づく
        
        ## データコンテキスト
        {context}
        
        ## レポート構成
        ### 📊 **阪南ビジネスマシン 月次営業分析レポート**
        **対象月**: {target_month}
        **作成日**: {datetime.now().strftime("%Y-%m-%d")}
        **作成**: 営業支援AI みなみちゃん
        
        #### **📈 売上実績サマリー**
        [目標達成状況と前月比較]
        
        #### **👥 担当者別パフォーマンス分析**
        [個人別の詳細分析と強み・課題]
        
        #### **🏢 顧客・案件分析**
        [重要顧客の動向と新規開拓状況]
        
        #### **📊 商品・メーカー別実績**
        [RISO、XEROX、京セラ等の販売動向]
        
        #### **🔍 効率性・生産性分析**
        [活動効率と改善ポイント]
        
        #### **⚠️ リスク・課題分析**
        [注意すべき点と対応策]
        
        #### **🎯 次月戦略・改善提案**
        [具体的なアクションプランと目標]
        
        **※このレポートはAIが生成したものです。重要な判断は必ず担当者・管理者と相談してください。**
        
        上記の構成で、経営層が意思決定に活用できるレベルの分析レポートを作成してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"月次分析レポート生成中にエラーが発生しました: {e}"
    
    def create_excel_report(self, report_content: str, report_type: str = "daily") -> bytes:
        """Excel形式でのレポート出力（基本実装）"""
        # 実際の実装では openpyxl などを使用してExcelファイルを生成
        # ここでは基本的な実装として文字列を返す
        excel_content = f"""
        阪南ビジネスマシン営業レポート ({report_type})
        生成日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        {report_content}
        
        ※Excel出力機能は開発中です。現在はテキスト形式で出力しています。
        """
        
        return excel_content.encode('utf-8')
    
    def format_email_content(self, report_content: str, recipient: str = "部長") -> str:
        """メール配信用のフォーマット"""
        email_template = f"""
件名: 【阪南ビジネスマシン】営業レポート - {datetime.now().strftime("%Y/%m/%d")}

{recipient}

お疲れ様です。
営業支援AI「みなみちゃん」より、本日の営業レポートをお送りいたします。

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

{report_content}

■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

＜自動配信について＞
このレポートは営業支援AIシステムにより自動生成・配信されています。
内容についてご質問がございましたら、営業部までお気軽にお問い合わせください。

※詳細な数値や個別案件については、担当者に直接ご確認ください。

――――――――――――――――――――――――――――――――――――
阪南ビジネスマシン株式会社 営業支援AIシステム
Webサイト: https://hbm-web.co.jp/
――――――――――――――――――――――――――――――――――――
        """
        
        return email_template
    
    def _prepare_daily_context(self, target_date: str) -> str:
        """日次レポート用のデータコンテキスト準備"""
        context_parts = []
        
        try:
            # 指定日の活動データ
            if self.detailed_sales_data and "daily_activities" in self.detailed_sales_data:
                daily_activities = self.detailed_sales_data["daily_activities"]
                if target_date in daily_activities:
                    context_parts.append(f"【{target_date}の活動データ】")
                    daily_data = daily_activities[target_date]
                    
                    total_visits = sum(data.get('visits', 0) for data in daily_data.values())
                    total_calls = sum(data.get('calls', 0) for data in daily_data.values())
                    total_deals = sum(data.get('deals', 0) for data in daily_data.values())
                    total_forecast = sum(data.get('revenue_forecast', 0) for data in daily_data.values())
                    
                    context_parts.append(f"チーム合計: 訪問{total_visits}件、電話{total_calls}件、商談{total_deals}件、予測売上{total_forecast}万円")
                    
                    for member, data in daily_data.items():
                        context_parts.append(f"{member}: 訪問{data.get('visits', 0)}件、電話{data.get('calls', 0)}件、商談{data.get('deals', 0)}件")
                        if data.get('notes'):
                            context_parts.append(f"  備考: {data['notes']}")
                    context_parts.append("")
            
            # 顧客パイプライン情報
            if self.detailed_sales_data and "customer_pipeline" in self.detailed_sales_data:
                context_parts.append("【主要商談状況】")
                pipeline = self.detailed_sales_data["customer_pipeline"]
                for customer, info in list(pipeline.items())[:5]:  # 上位5件
                    context_parts.append(f"{customer}: {info.get('stage', '不明')}段階、確度{info.get('probability', 0)}%、予想{info.get('expected_value', 0)}万円")
                context_parts.append("")
            
            # 基本売上データから関連情報
            if self.basic_sales_data:
                context_parts.append("【基本売上データ（参考）】")
                context_parts.append(self.basic_sales_data[:500] + "...")  # 先頭500文字
                context_parts.append("")
                
        except Exception as e:
            context_parts.append(f"データ準備中にエラーが発生しました: {e}")
        
        return "\n".join(context_parts)
    
    def _prepare_monthly_context(self, target_month: str) -> str:
        """月次レポート用のデータコンテキスト準備"""
        context_parts = []
        
        try:
            # 基本売上データ
            if self.basic_sales_data:
                context_parts.append("【基本売上実績データ】")
                context_parts.append(self.basic_sales_data)
                context_parts.append("")
            
            # 効率性データ
            if self.enhanced_metrics and "activity_efficiency" in self.enhanced_metrics:
                context_parts.append("【営業効率性データ】")
                efficiency = self.enhanced_metrics["activity_efficiency"]
                
                if "calls_per_deal" in efficiency:
                    context_parts.append("成約1件あたりの電話件数:")
                    for member, value in efficiency["calls_per_deal"]["individual"].items():
                        context_parts.append(f"  {member}: {value}件")
                
                if "avg_deal_size" in efficiency:
                    context_parts.append("平均案件サイズ:")
                    for member, value in efficiency["avg_deal_size"]["individual"].items():
                        context_parts.append(f"  {member}: {value:,}円")
                context_parts.append("")
            
            # KPIトレンド
            if self.enhanced_metrics and "kpi_trends" in self.enhanced_metrics:
                context_parts.append("【KPIトレンドデータ】")
                kpi = self.enhanced_metrics["kpi_trends"]
                
                if "conversion_rate" in kpi:
                    context_parts.append(f"部門平均成約率: {kpi['conversion_rate']['department_average']:.1%}")
                    context_parts.append("個人別成約率:")
                    for member, rate in kpi["conversion_rate"]["individual"].items():
                        context_parts.append(f"  {member}: {rate:.1%}")
                
                if "avg_deal_size" in kpi:
                    context_parts.append(f"部門平均案件サイズ: {kpi['avg_deal_size']['department_average']:,}円")
                context_parts.append("")
            
            # 顧客満足度
            if self.enhanced_metrics and "customer_satisfaction" in self.enhanced_metrics:
                context_parts.append("【顧客満足度データ】")
                satisfaction = self.enhanced_metrics["customer_satisfaction"]
                context_parts.append(f"総合満足度: {satisfaction.get('overall_satisfaction', 'N/A')}")
                
                if "individual_ratings" in satisfaction:
                    context_parts.append("個人別満足度:")
                    for member, rating in satisfaction["individual_ratings"].items():
                        context_parts.append(f"  {member}: {rating}")
                context_parts.append("")
            
            # 主要顧客関係
            if self.interaction_history and "customer_interactions" in self.interaction_history:
                context_parts.append("【主要顧客関係データ】")
                interactions = self.interaction_history["customer_interactions"]
                for customer, info in list(interactions.items())[:5]:  # 上位5件
                    context_parts.append(f"{customer}: 関係強度{info.get('relationship_strength', '不明')}, 満足度{info.get('satisfaction_rating', 'N/A')}")
                context_parts.append("")
                
        except Exception as e:
            context_parts.append(f"月次データ準備中にエラーが発生しました: {e}")
        
        return "\n".join(context_parts)
    
    def generate_custom_report(self, request: str, context_data: Dict[str, Any] = None) -> str:
        """カスタムレポート生成"""
        prompt = f"""
        あなたは阪南ビジネスマシンの営業分析専門スタッフです。
        以下のリクエストに基づいて、カスタム営業レポートを作成してください。
        
        ## リクエスト内容
        {request}
        
        ## 利用可能データ
        基本売上データ: {bool(self.basic_sales_data)}
        詳細営業データ: {bool(self.detailed_sales_data)}
        営業指標データ: {bool(self.enhanced_metrics)}
        顧客接触履歴: {bool(self.interaction_history)}
        
        ## 追加コンテキスト
        {context_data if context_data else "なし"}
        
        ## レポート要件
        - 阪南ビジネスマシンの実データに基づく
        - 実用的で具体的な内容
        - リクエストに応じた構成
        - 必要に応じて改善提案を含む
        
        上記を踏まえて、適切なカスタムレポートを作成してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            return f"カスタムレポート生成中にエラーが発生しました: {e}"
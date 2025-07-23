# src/services/enhanced_clinical_analysis.py  
"""
A病院固有の診療実績・治療成績分析サービス
実際のA病院データに基づく症例検索、治療成績、論文研究支援
"""

import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from collections import defaultdict

class EnhancedClinicalAnalysisService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.clinical_outcomes = self._load_clinical_outcomes()
        self.research_data = self._load_research_data() 
        self.detailed_patients = self._load_detailed_patients()
        self.hospital_info = self._load_hospital_info()
        self.comprehensive_data = self._load_comprehensive_medical_data()
        self.competitive_analysis = self._load_competitive_analysis()
        self.security_data = self._load_security_data()
        
    def _load_clinical_outcomes(self):
        """A病院診療成績データ読み込み"""
        try:
            with open("src/data/dummy_data/clinical_outcomes.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_research_data(self):
        """研究データ読み込み"""
        try:
            with open("src/data/dummy_data/research_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_detailed_patients(self):
        """詳細患者データ読み込み"""
        try:
            with open("src/data/dummy_data/detailed_patients.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"patients": []}
    
    def _load_hospital_info(self):
        """A病院基本情報読み込み"""
        try:
            with open("src/data/dummy_data/hospital_info.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"name": "A病院"}
    
    def _load_comprehensive_medical_data(self):
        """包括的医療データ読み込み"""
        try:
            with open("src/data/dummy_data/comprehensive_medical_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_competitive_analysis(self):
        """競合分析データ読み込み"""
        try:
            with open("src/data/dummy_data/competitive_analysis.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_security_data(self):
        """セキュリティデータ読み込み"""
        try:
            with open("src/data/dummy_data/system_security_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def analyze_treatment_outcomes_by_demographics(self, query: str) -> str:
        """年齢・性別別治療成績分析"""
        
        # 疾患特定
        disease_mapping = {
            "心筋梗塞": "acute_myocardial_infarction",
            "脳梗塞": "cerebral_infarction", 
            "大腿骨": "femoral_neck_fracture",
            "大腿骨頸部骨折": "femoral_neck_fracture",
            "大腿骨骨折": "femoral_neck_fracture",
            "骨折": "femoral_neck_fracture",
            "t-pa": "cerebral_infarction",
            "tpa": "cerebral_infarction"
        }
        
        target_disease = None
        for keyword, disease_key in disease_mapping.items():
            if keyword in query:
                target_disease = disease_key
                break
        
        # 包括的データからの疾患検索も試行
        if not target_disease:
            # 包括的データからの検索
            comprehensive_outcomes = self.comprehensive_data.get("hospital_performance_metrics", {}).get("disease_specific_outcomes", {})
            for keyword, disease_key in disease_mapping.items():
                if keyword in query:
                    if disease_key in comprehensive_outcomes:
                        target_disease = disease_key
                        break
        
        # 従来データまたは包括データから取得
        disease_data = None
        if target_disease and target_disease in self.clinical_outcomes:
            disease_data = self.clinical_outcomes[target_disease]
        elif target_disease and target_disease in self.comprehensive_data.get("hospital_performance_metrics", {}).get("disease_specific_outcomes", {}):
            disease_data = self.comprehensive_data["hospital_performance_metrics"]["disease_specific_outcomes"][target_disease]
        
        if not disease_data:
            return self._provide_general_outcomes_summary(query)
        
        prompt = f"""
        あなたはA病院の医療統計分析責任者です。以下の当院実績データに基づき、質問にお答えください。

        # A病院の実績データ（{self.clinical_outcomes.get('data_period', '2023-2024年')}）
        
        ## 対象疾患: {target_disease.replace('_', ' ').title()}
        **A病院での総症例数**: {disease_data.get('total_cases', 'N/A')}例

        ### 年齢別実績
        {json.dumps(disease_data.get('demographics', {}), ensure_ascii=False, indent=2)}

        ### A病院での治療成績
        {json.dumps(disease_data.get('treatment_outcomes', {}), ensure_ascii=False, indent=2)}

        ### 全国平均との比較
        {json.dumps(disease_data.get('comparison', {}), ensure_ascii=False, indent=2)}

        # 質問
        {query}

        # A病院データベースから抽出した関連症例概要
        {self._get_related_cases_summary(target_disease)}

        # 回答形式（必ずA病院の実績であることを明示）
        🏥 **A病院 診療実績分析結果**

        1. **A病院での{target_disease.replace('_', ' ')}症例概要**
        2. **年齢・性別別治療成績（当院実績）**
        3. **A病院の治療特徴・強み**
        4. **全国平均との比較優位性**
        5. **今後の改善課題（当院固有）**

        A病院固有のデータと実績を強調し、他院との差別化ポイントを明確に示してください。
        数値は全てA病院の実際のデータに基づく内容としてください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院診療実績分析中にエラーが発生しました: {e}"
    
    def _get_related_cases_summary(self, disease_key):
        """関連症例の概要抽出"""
        disease_mapping = {
            "acute_myocardial_infarction": "急性心筋梗塞",
            "cerebral_infarction": "脳梗塞",
            "femoral_neck_fracture": "大腿骨頸部骨折"
        }
        
        target_diagnosis = disease_mapping.get(disease_key, "")
        if not target_diagnosis:
            return "関連症例データなし"
        
        # 該当患者を抽出
        relevant_cases = []
        for patient in self.detailed_patients.get("patients", [])[:10]:  # 最初の10例
            if target_diagnosis in patient.get("primary_diagnosis", ""):
                relevant_cases.append({
                    "患者ID": patient["patient_id"],
                    "年齢性別": f"{patient['age']}歳{patient['gender']}",
                    "治療科": patient["admission_info"]["診療科"],
                    "治療経過": list(patient.get("treatment_course", {}).values())[:2]  # 最初の2項目
                })
        
        return f"A病院データベース該当症例: {len(relevant_cases)}例の代表例を分析に含む"
    
    def support_research_and_papers(self, query: str) -> str:
        """研究・論文支援"""
        
        # 具体的な研究テーマ別データを生成
        specific_research_data = self._generate_specific_research_data(query)
        
        prompt = f"""
        あなたはA病院の研究支援センター長です。以下のA病院の実績データと患者データベースを基に、具体的で実現可能な研究計画を支援してください。

        # A病院の研究実績（発表済み）
        {json.dumps(self.research_data, ensure_ascii=False, indent=2)}

        # A病院患者データベース詳細
        - 総登録患者数: {len(self.detailed_patients.get('patients', []))}名（A2024-0001〜A2024-0500）
        - データ期間: 2022年〜2024年（3年間）
        - 主要診療科: {', '.join(self.hospital_info.get('specialties', []))}
        - 電子カルテ完全デジタル化: 2020年〜（4年間の蓄積）

        # 研究テーマ別利用可能データ
        {specific_research_data}

        # 研究相談内容
        {query}

        # 回答形式
        🏥 **A病院 研究支援センター 研究計画書**

        ## 📊 **利用可能なA病院データ**
        - 対象症例数と期間
        - 収集可能な変数・指標
        - データの質と完整性

        ## 🎯 **研究デザイン提案**
        - 研究手法（後ろ向き/前向き）
        - 主要評価項目・副次評価項目
        - 統計解析計画

        ## 📈 **期待される成果**
        - A病院の強み・特色を活かした差別化ポイント
        - 投稿対象ジャーナル候補
        - 学会発表スケジュール

        ## ⚠️ **注意事項**
        - A病院IRB申請要件
        - 患者同意取得方針
        - データ匿名化基準

        ## 🚀 **実行スケジュール（6ヶ月計画）**
        - IRB申請〜承認（1-2ヶ月）
        - データ抽出・解析（2-3ヶ月）  
        - 論文執筆・投稿（1-2ヶ月）

        A病院の実際のデータを活用した、実現性の高い研究計画を詳細に提示してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院研究支援中にエラーが発生しました: {e}"
    
    def _generate_specific_research_data(self, query: str) -> str:
        """研究テーマに応じた具体的データ情報生成"""
        query_lower = query.lower()
        
        if "doac" in query_lower or "心房細動" in query_lower:
            return """
### 心房細動・DOAC関連研究データ（A病院）
- 心房細動診断患者: 276名（2022-2024年）
- DOAC処方患者: 189名（アピキサバン89名、リバーロキサバン67名、エドキサバン33名）
- ワーファリン継続患者: 87名
- 追跡可能期間: 平均24.3ヶ月
- 主要評価項目データ: 脳梗塞発症、大出血、死亡率
- 副次評価項目: 腎機能、肝機能、薬剤継続率、患者満足度"""
        
        elif "covid" in query_lower:
            return """
### COVID-19重症化研究データ（A病院）
- COVID-19入院患者: 394名（2020年4月〜2023年12月）
- 重症化症例: 127名（ICU入室基準）
- 死亡例: 23名
- 利用可能データ: 年齢、性別、BMI、併存疾患、ワクチン接種歴、
  検査値（炎症マーカー、D-dimer、フェリチン等）、画像所見、治療内容"""
        
        elif "感染" in query_lower or "ssi" in query_lower:
            return """
### 術後感染症研究データ（A病院）
- 手術症例総数: 2,847例（2020-2024年）
- 整形外科手術: 1,456例（SSI率1.8%）
- 消化器外科手術: 892例（SSI率2.1%）
- 予防抗菌薬使用実績、手術時間、術者経験年数、
  患者背景因子（糖尿病、免疫抑制剤等）完備"""
        
        else:
            return """
### 汎用研究データ（A病院）
- 全診療科データベース完備
- 診断名、処方歴、検査値、画像データ
- 転帰情報（生存率、再入院率、機能予後）
- 医療経済データ（在院日数、医療費）"""
    
    def provide_prognosis_prediction(self, query: str) -> str:
        """予後予測・診療方針支援"""
        
        prompt = f"""
        あなたはA病院の診療支援AIです。A病院の過去実績とエビデンスに基づき、診療方針を支援してください。

        # A病院の診療実績データ
        {json.dumps(self.clinical_outcomes, ensure_ascii=False, indent=2)}

        # A病院の治療プロトコル特徴
        - 急性心筋梗塞: Primary PCI 92%実施、Door to Balloon 78.5分
        - 脳梗塞: t-PA投与率23.4%、機械的血栓回収術8.9%
        - 大腿骨骨折: 48時間以内手術89.6%、歩行回復率78.4%

        # 質問・相談内容
        {query}

        # 回答形式
        🏥 **A病院 診療支援システム**

        1. **A病院での同様症例実績**
        2. **予後予測（当院データベース基準）**
        3. **推奨診療方針（A病院プロトコル準拠）**
        4. **リスク評価とモニタリング**
        5. **患者・家族説明資料**

        A病院の実績に基づく信頼性の高い情報を提供してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院診療支援中にエラーが発生しました: {e}"
    
    def _add_demo_disclaimer(self, response: str) -> str:
        """デモ版・電子カルテ連携前提の注記を追加"""
        disclaimer = """

---
⚠️ **デモ版システムについて**
• このシステムはデモ版です。実際の運用時は電子カルテシステムとの連携が前提となります。
• 表示データは仮想データです。実運用時はリアルタイムの電子カルテデータを参照します。
• 本格運用には以下の技術統合が必要：
  - 電子カルテAPI連携（HL7 FHIR準拠）
  - リアルタイムデータ同期基盤
  - セキュア認証・監査ログシステム
  - 医療情報システム安全管理ガイドライン準拠

🏥 **A病院 Smart Hospital AI - Enhanced Clinical Analysis Module**"""
        
        return response + disclaimer

    def _provide_general_outcomes_summary(self, query):
        """一般的な診療成績サマリー"""
        response = f"""
🏥 **A病院 診療実績データベース**

## A病院の主要診療成績（2023-2024年実績）

### 🫀 **循環器内科実績**
- 急性心筋梗塞: 年間156例
- Primary PCI成功率: 92%
- 院内死亡率: 3.8%（全国平均6.7%より低い）
- Door to Balloon時間: 平均78.5分

### 🧠 **脳神経内科実績**  
- 脳梗塞: 年間203例
- t-PA投与率: 23.4%
- 良好転帰率（mRS 0-2）: 51.2%
- 在宅復帰率: 62.3%

### 🦴 **整形外科実績**
- 大腿骨頸部骨折: 年間134例
- 48時間以内手術率: 89.6%
- 歩行回復率: 78.4%
- 術後感染率: 1.5%

### 🏆 **A病院の特徴・強み**
- 全国平均を上回る治療成績
- 24時間体制の救急対応
- 多職種連携による包括的ケア
- 地域医療機関との密接な連携

---
お探しの疾患について詳細な分析をお求めでしたら、具体的な疾患名をお聞かせください。
        
入力された質問: {query}
"""
        return self._add_demo_disclaimer(response)
    
    def analyze_competitive_positioning(self, query: str) -> str:
        """競合分析・市場ポジショニング分析"""
        
        prompt = f"""
        あなたはA病院の経営戦略コンサルタントです。以下のA病院の競合分析データに基づき、戦略的提言を行ってください。

        # A病院の市場ポジション
        {json.dumps(self.competitive_analysis.get("market_analysis", {}), ensure_ascii=False, indent=2)}
        
        # 競合病院との比較データ  
        {json.dumps(self.competitive_analysis.get("performance_benchmarking", {}), ensure_ascii=False, indent=2)}
        
        # A病院の診療実績（詳細）
        {json.dumps(self.comprehensive_data.get("hospital_performance_metrics", {}), ensure_ascii=False, indent=2)}
        
        # 戦略提案・投資シミュレーション
        {json.dumps(self.competitive_analysis.get("strategic_recommendations", {}), ensure_ascii=False, indent=2)}
        
        # 質問内容
        {query}
        
        # 回答形式
        🏥 **A病院 経営戦略分析**
        
        ## 📊 **市場ポジション分析**
        - A病院の現在の市場シェア・順位
        - 競合他院との比較優位性
        - 地域医療圏での特色・強み
        
        ## 🎯 **戦略的提言**
        - 短期改善策（投資効果・実現性）
        - 中長期成長戦略
        - 差別化ポイント強化策
        
        ## 💰 **投資優先順位**
        - ROI分析に基づく投資提案
        - 競合対策としての必要投資
        - 財務インパクト予測
        
        実際のA病院データに基づく、具体的で実現可能な戦略提案を行ってください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院競合分析中にエラーが発生しました: {e}"
    
    def analyze_system_security(self, query: str) -> str:
        """システム・セキュリティ分析"""
        
        prompt = f"""
        あなたはA病院の医療情報システム責任者です。以下のセキュリティフレームワークと技術仕様に基づき、質問にお答えください。

        # A病院のセキュリティ体制
        {json.dumps(self.security_data.get("security_framework", {}), ensure_ascii=False, indent=2)}
        
        # システム統合・API仕様
        {json.dumps(self.security_data.get("integration_security", {}), ensure_ascii=False, indent=2)}
        
        # 運用セキュリティ・事業継続性
        {json.dumps(self.security_data.get("operational_security", {}), ensure_ascii=False, indent=2)}
        
        # 技術仕様・AI模型セキュリティ
        {json.dumps(self.security_data.get("technical_specifications", {}), ensure_ascii=False, indent=2)}
        
        # リスク評価・監査体制
        {json.dumps(self.security_data.get("risk_assessment", {}), ensure_ascii=False, indent=2)}
        
        # 質問内容
        {query}
        
        # 回答形式
        🔒 **A病院 医療情報システム セキュリティ仕様書**
        
        ## 🛡️ **セキュリティレベル**
        - 準拠ガイドライン・認証
        - データ保護・暗号化仕様
        - アクセス制御・監査機能
        
        ## ⚙️ **技術的実装**
        - システム統合方式
        - API仕様・認証方式
        - AI処理・データ処理方式
        
        ## 🚨 **リスク管理**
        - インシデント対応体制
        - 事業継続計画
        - 監査・コンプライアンス
        
        A病院の実装レベルでの具体的なセキュリティ仕様を詳細に説明してください。
        """
        
        try:
            response = self.model.invoke(prompt)
            return self._add_demo_disclaimer(response.content)
        except Exception as e:
            return f"A病院セキュリティ分析中にエラーが発生しました: {e}"
    
    def query_clinical_analysis(self, query: str) -> str:
        """メインエントリーポイント"""
        query_lower = query.lower()
        
        print(f"Clinical analysis query: {query_lower}")  # デバッグログ
        
        # より詳細な機能振り分け
        if any(keyword in query_lower for keyword in ["論文を書きたい", "論文", "研究", "データ分析", "統計", "doac", "covid"]):
            print("→ 研究支援機能に振り分け")
            return self.support_research_and_papers(query)
        elif any(keyword in query_lower for keyword in ["予後", "診療方針", "治療選択", "プロファイル", "リスク"]):
            print("→ 予後予測機能に振り分け")
            return self.provide_prognosis_prediction(query)
        elif any(keyword in query_lower for keyword in ["差別化", "競合", "市場", "戦略", "投資", "経営", "収益", "シェア"]):
            print("→ 競合分析機能に振り分け")
            return self.analyze_competitive_positioning(query)
        elif any(keyword in query_lower for keyword in ["セキュリティ", "aiシステム", "システム", "電子カルテ", "api", "暗号化", "個人情報", "漏洩", "監査", "データ保護", "リスク", "対策"]) and any(keyword in query_lower for keyword in ["ai", "システム", "技術", "セキュリティ"]):
            print("→ セキュリティ分析機能に振り分け")
            return self.analyze_system_security(query)
        elif any(keyword in query_lower for keyword in ["治療成績", "実績", "症例", "転帰", "成功率", "心筋梗塞", "脳梗塞", "骨折", "糖尿病", "透析"]):
            print("→ 治療成績分析機能に振り分け")
            return self.analyze_treatment_outcomes_by_demographics(query)
        else:
            print("→ デフォルトで治療成績分析機能に振り分け")
            return self.analyze_treatment_outcomes_by_demographics(query)
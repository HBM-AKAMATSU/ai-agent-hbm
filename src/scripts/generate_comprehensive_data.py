#!/usr/bin/env python3
"""
A病院固有の包括的ダミーデータ生成スクリプト
患者固有データ、診療実績、研究データなどを生成
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker('ja_JP')

class ComprehensiveHospitalDataGenerator:
    def __init__(self):
        self.data_dir = "src/data/dummy_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # A病院の基本情報
        self.hospital_info = {
            "name": "A病院",
            "beds": 280,
            "established": "1985年",
            "type": "急性期総合病院",
            "location": "東京都中央区",
            "specialties": [
                "循環器内科", "心臓血管外科", "脳神経内科", "脳神経外科", 
                "整形外科", "消化器内科", "消化器外科", "呼吸器内科",
                "腎臓内科", "糖尿病内科", "救急科", "麻酔科"
            ]
        }
        
        # 疾患別治療プロトコル
        self.treatment_protocols = {
            "急性心筋梗塞": {
                "標準治療": "Primary PCI（90分以内）",
                "薬物療法": "DAPT + スタチン + ACE阻害薬",
                "入院期間": "7-10日",
                "合併症管理": "心不全、不整脈、機械的合併症"
            },
            "脳梗塞": {
                "急性期治療": "t-PA投与（4.5時間以内）または血管内治療",
                "二次予防": "抗血小板薬、リハビリテーション",
                "入院期間": "14-21日",
                "連携": "回復期リハ病院との地域連携"
            },
            "大腿骨頸部骨折": {
                "手術方針": "人工骨頭置換術または骨接合術",
                "麻酔": "脊椎麻酔優先、術前評価重視",
                "リハビリ": "術後翌日から理学療法開始",
                "退院支援": "在宅復帰率80%目標"
            }
        }
    
    def generate_detailed_patients(self, count=500):
        """A2024-XXXX形式の詳細な患者データ生成"""
        patients = []
        
        for i in range(1, count + 1):
            patient_id = f"A2024-{i:04d}"
            
            # 基本情報
            age = random.randint(20, 95)
            gender = random.choice(["男性", "女性"])
            
            # 主訴・診断
            if age >= 60:
                primary_diagnosis = random.choice([
                    "急性心筋梗塞", "狭心症", "心房細動", "脳梗塞", "脳出血",
                    "大腿骨頸部骨折", "糖尿病", "高血圧", "慢性腎臓病", "COPD"
                ])
            else:
                primary_diagnosis = random.choice([
                    "胆石症", "虫垂炎", "外傷", "肺炎", "消化器疾患"
                ])
            
            # 既往歴（年齢と関連）
            medical_history = []
            if age > 50:
                possible_history = ["高血圧", "糖尿病", "脂質異常症", "心疾患", "脳血管疾患"]
                medical_history = random.sample(possible_history, random.randint(0, 3))
            
            # アレルギー歴
            allergies = []
            if random.random() < 0.25:  # 25%の確率
                allergy_list = [
                    "ペニシリン", "セフェム系抗生物質", "造影剤", "ヨード",
                    "NSAIDs", "アスピリン", "卵", "そば", "エビ・カニ"
                ]
                allergies = random.sample(allergy_list, random.randint(1, 2))
            
            # 現在の処方薬
            current_medications = self._generate_medications_for_diagnosis(primary_diagnosis, medical_history)
            
            # 検査値
            lab_values = self._generate_lab_values(primary_diagnosis, age)
            
            # 治療経過
            treatment_course = self._generate_treatment_course(primary_diagnosis)
            
            # 入院情報
            admission_info = {
                "入院日": fake.date_between(start_date='-90d', end_date='today').isoformat(),
                "診療科": self._get_department_for_diagnosis(primary_diagnosis),
                "主治医": f"Dr.{random.choice(['田中', '佐藤', '高橋', '山田', '渡辺'])}{random.randint(1,9):02d}",
                "病床": f"{random.randint(3,8)}階{random.choice(['A','B','C'])}病棟"
            }
            
            patient = {
                "patient_id": patient_id,
                "name": fake.name(),
                "age": age,
                "gender": gender,
                "primary_diagnosis": primary_diagnosis,
                "medical_history": medical_history,
                "allergies": allergies,
                "current_medications": current_medications,
                "lab_values": lab_values,
                "treatment_course": treatment_course,
                "admission_info": admission_info,
                "hospital": "A病院",
                "created_date": fake.date_between(start_date='-2y', end_date='today').isoformat()
            }
            
            patients.append(patient)
        
        return patients
    
    def _generate_medications_for_diagnosis(self, diagnosis, history):
        """診断に基づく処方薬生成"""
        medications = []
        
        if diagnosis == "急性心筋梗塞":
            medications = [
                "アスピリン 100mg 1錠/日",
                "クロピドグレル 75mg 1錠/日", 
                "アトルバスタチン 20mg 1錠/日",
                "リシノプリル 5mg 1錠/日"
            ]
        elif diagnosis == "心房細動":
            medications = [
                "ワーファリン 2mg 1錠/日",  # または
                random.choice(["アピキサバン 5mg 2錠/日", "リバーロキサバン 15mg 1錠/日"]),
                "ビソプロロール 2.5mg 1錠/日"
            ]
        elif diagnosis == "脳梗塞":
            medications = [
                "アスピリン 100mg 1錠/日",
                "アトルバスタチン 20mg 1錠/日",
                "テルミサルタン 40mg 1錠/日"
            ]
        elif "高血圧" in history:
            medications.append("アムロジピン 5mg 1錠/日")
        elif "糖尿病" in history:
            medications.append("メトホルミン 500mg 2錠/日")
            
        return medications[:4]  # 最大4剤まで
    
    def _generate_lab_values(self, diagnosis, age):
        """診断に基づく検査値生成"""
        base_values = {
            "WBC": random.uniform(4000, 10000),
            "RBC": random.uniform(400, 550) if random.choice(["男性", "女性"]) == "男性" else random.uniform(380, 480),
            "Plt": random.uniform(150000, 400000),
            "TP": random.uniform(6.5, 8.0),
            "Alb": random.uniform(3.5, 5.0),
            "T-Bil": random.uniform(0.3, 1.2),
            "AST": random.uniform(15, 40),
            "ALT": random.uniform(10, 40),
            "LDH": random.uniform(120, 240),
            "γ-GTP": random.uniform(10, 50),
            "BUN": random.uniform(8, 22),
            "Cre": random.uniform(0.6, 1.2),
            "eGFR": random.uniform(60, 120),
            "UA": random.uniform(3.0, 7.0),
            "T-Cho": random.uniform(150, 220),
            "TG": random.uniform(50, 150),
            "HDL-C": random.uniform(40, 80),
            "LDL-C": random.uniform(80, 140),
            "BS": random.uniform(80, 120),
            "HbA1c": random.uniform(4.5, 6.0),
            "CRP": random.uniform(0.0, 0.3),
            "PT-INR": random.uniform(0.9, 1.1)
        }
        
        # 診断に応じて異常値を設定
        if diagnosis == "急性心筋梗塞":
            base_values["CK"] = random.uniform(500, 3000)
            base_values["CK-MB"] = random.uniform(50, 300)
            base_values["トロポニンT"] = random.uniform(0.5, 10.0)
            base_values["BNP"] = random.uniform(100, 800)
        elif diagnosis == "脳梗塞":
            base_values["CRP"] = random.uniform(0.5, 5.0)
            base_values["D-dimer"] = random.uniform(1.0, 5.0)
        elif "腎" in diagnosis:
            base_values["Cre"] = random.uniform(1.2, 3.0)
            base_values["eGFR"] = random.uniform(15, 59)
            base_values["BUN"] = random.uniform(20, 60)
        
        return {k: round(v, 2) for k, v in base_values.items()}
    
    def _generate_treatment_course(self, diagnosis):
        """診断に基づく治療経過"""
        if diagnosis == "急性心筋梗塞":
            return {
                "来院時": "胸痛、冷汗、ST上昇",
                "治療": "Primary PCI施行、#6 99%狭窄にDES留置",
                "経過": "術後経過良好、心機能改善",
                "退院時": "LVEF 50%、リハビリ継続"
            }
        elif diagnosis == "脳梗塞":
            return {
                "来院時": "右片麻痺、構音障害、NIHSS 8点",
                "治療": "t-PA投与、抗血小板療法開始",
                "経過": "神経症状改善傾向、嚥下機能評価",
                "退院時": "mRS 2、回復期リハ病院転院"
            }
        elif diagnosis == "大腿骨頸部骨折":
            return {
                "来院時": "転倒後の右股関節痛、歩行不可",
                "治療": "人工骨頭置換術施行",
                "経過": "術後疼痛管理、早期離床",
                "退院時": "歩行器歩行可能、自宅退院"
            }
        else:
            return {
                "来院時": "症状安定",
                "治療": "保存的加療",
                "経過": "経過良好",
                "退院時": "自宅退院"
            }
    
    def _get_department_for_diagnosis(self, diagnosis):
        """診断に対応する診療科"""
        mapping = {
            "急性心筋梗塞": "循環器内科",
            "狭心症": "循環器内科",
            "心房細動": "循環器内科",
            "脳梗塞": "脳神経内科",
            "脳出血": "脳神経外科",
            "大腿骨頸部骨折": "整形外科",
            "糖尿病": "糖尿病内科",
            "高血圧": "循環器内科",
            "慢性腎臓病": "腎臓内科",
            "COPD": "呼吸器内科",
            "肺炎": "呼吸器内科"
        }
        return mapping.get(diagnosis, "内科")
    
    def generate_clinical_outcomes_data(self):
        """A病院の診療成績データ生成"""
        outcomes = {
            "hospital_name": "A病院",
            "data_period": "2023年1月〜2024年12月",
            "acute_myocardial_infarction": {
                "total_cases": 156,
                "demographics": {
                    "50代": {"cases": 28, "male": 24, "female": 4},
                    "60代": {"cases": 45, "male": 32, "female": 13},
                    "70代": {"cases": 52, "male": 31, "female": 21},
                    "80代以上": {"cases": 31, "male": 15, "female": 16}
                },
                "treatment_outcomes": {
                    "primary_pci_rate": 0.92,  # 92%
                    "door_to_balloon_time": 78.5,  # 分
                    "in_hospital_mortality": 0.038,  # 3.8%
                    "30day_mortality": 0.051,  # 5.1%
                    "major_complications": 0.083,  # 8.3%
                    "average_los": 8.2,  # 日
                    "lvef_at_discharge": 48.7  # %
                },
                "comparison": {
                    "national_average_mortality": 0.067,
                    "national_average_los": 11.5,
                    "a_hospital_advantage": "死亡率が全国平均より2.9%低い"
                }
            },
            "cerebral_infarction": {
                "total_cases": 203,
                "demographics": {
                    "60代": {"cases": 48, "mild": 22, "moderate": 18, "severe": 8},
                    "70代": {"cases": 89, "mild": 35, "moderate": 38, "severe": 16},
                    "80代以上": {"cases": 66, "mild": 20, "moderate": 28, "severe": 18}
                },
                "treatment_outcomes": {
                    "tpa_administration_rate": 0.234,  # 23.4%
                    "mechanical_thrombectomy_rate": 0.089,  # 8.9%
                    "favorable_outcome_mrs_0_2": 0.512,  # 51.2%
                    "in_hospital_mortality": 0.074,  # 7.4%
                    "average_los": 18.6,  # 日
                    "home_discharge_rate": 0.623  # 62.3%
                },
                "rehabilitation": {
                    "acute_phase_rehab": 0.95,
                    "speech_therapy_cases": 89,
                    "functional_improvement": 0.73
                }
            },
            "femoral_neck_fracture": {
                "total_cases": 134,
                "demographics": {
                    "70代": {"cases": 48, "bipolar": 32, "osteosynthesis": 16},
                    "80代": {"cases": 86, "bipolar": 71, "osteosynthesis": 15}
                },
                "treatment_outcomes": {
                    "surgery_within_48h": 0.896,  # 89.6%
                    "surgical_success_rate": 0.955,  # 95.5%
                    "walking_recovery_rate": 0.784,  # 78.4%
                    "home_discharge_rate": 0.657,  # 65.7%
                    "in_hospital_mortality": 0.022,  # 2.2%
                    "average_los": 21.3,  # 日
                    "rehabilitation_days": 14.8
                },
                "complications": {
                    "surgical_site_infection": 0.015,
                    "dislocation": 0.037,
                    "deep_vein_thrombosis": 0.052
                }
            }
        }
        
        return outcomes
    
    def generate_research_data(self):
        """A病院の研究・論文データ"""
        research_data = {
            "hospital": "A病院",
            "research_period": "2020-2024年",
            "publications": [
                {
                    "title": "A病院における急性心筋梗塞患者のDOAC使用実績と安全性の検討",
                    "journal": "日本循環器学会誌",
                    "year": 2024,
                    "cases": 89,
                    "findings": "DOAC使用例では出血合併症が有意に少なく、再梗塞率も低下"
                },
                {
                    "title": "COVID-19重症化因子の多施設共同研究：A病院での312例の解析",
                    "journal": "日本感染症学会誌", 
                    "year": 2023,
                    "cases": 312,
                    "findings": "年齢、糖尿病、腎機能低下が独立した重症化因子"
                },
                {
                    "title": "整形外科手術部位感染の5年間疫学調査：A病院単施設研究",
                    "journal": "日本整形外科感染症学会誌",
                    "year": 2023,
                    "cases": 1456,
                    "findings": "SSI率1.8%、MRSA検出率低下傾向"
                }
            ],
            "ongoing_studies": [
                "脳梗塞急性期リハビリテーションの効果検証",
                "高齢者大腿骨骨折の在宅復帰促進プログラム",
                "心房細動患者の抗凝固薬選択指針の最適化"
            ]
        }
        
        return research_data
    
    def generate_hospital_protocols(self):
        """A病院固有のプロトコル・ガイドライン"""
        protocols = {
            "hospital": "A病院",
            "anticoagulation_protocol": {
                "warfarin_initiation": {
                    "starting_dose": "2mg/日（70歳未満）、1mg/日（70歳以上）",
                    "target_inr": {
                        "atrial_fibrillation": "2.0-3.0",
                        "mechanical_valve": "2.5-3.5"
                    },
                    "monitoring": "開始後3日、1週、2週、その後月1回",
                    "drug_interactions": [
                        "NSAIDs併用時は消化管出血リスク評価必須",
                        "アゾール系抗真菌薬併用時はワーファリン50%減量",
                        "抗生物質併用時は週2回INRモニタリング"
                    ]
                },
                "contrast_allergy_protocol": {
                    "screening": "問診票＋過去のアレルギー反応歴確認",
                    "premedication": "プレドニゾロン30mg（検査12時間前・2時間前）",
                    "emergency_preparation": "エピネフリン、ステロイド、抗ヒスタミン薬常備",
                    "post_observation": "検査後30分間バイタル監視"
                }
            },
            "surgical_protocols": {
                "femoral_neck_fracture": {
                    "anesthesia_preference": "脊椎麻酔優先（心機能評価後決定）",
                    "antibiotic_prophylaxis": "セファゾリン2g（30分前投与）",
                    "dvt_prevention": "術後6時間以内に抗凝固薬開始",
                    "rehabilitation": "術後翌日から段階的離床プログラム"
                }
            },
            "emergency_protocols": {
                "stroke_code": {
                    "activation_criteria": "FAST陽性または意識障害",
                    "target_times": {
                        "ct_completion": "15分以内",
                        "neurologist_evaluation": "20分以内", 
                        "tpa_decision": "30分以内"
                    },
                    "exclusion_criteria": "A病院独自チェックリスト使用"
                }
            }
        }
        
        return protocols
    
    def save_all_enhanced_data(self):
        """全ての拡張データを保存"""
        print("A病院固有の包括的データ生成を開始します...")
        
        # 1. 詳細患者データ
        print("詳細患者データ（A2024-XXXX形式）を生成中...")
        detailed_patients = self.generate_detailed_patients(500)
        with open(os.path.join(self.data_dir, "detailed_patients.json"), "w", encoding="utf-8") as f:
            json.dump({"patients": detailed_patients, "hospital": "A病院"}, f, ensure_ascii=False, indent=2)
        
        # 2. 診療成績データ
        print("A病院診療成績データを生成中...")
        outcomes = self.generate_clinical_outcomes_data()
        with open(os.path.join(self.data_dir, "clinical_outcomes.json"), "w", encoding="utf-8") as f:
            json.dump(outcomes, f, ensure_ascii=False, indent=2)
        
        # 3. 研究データ
        print("研究・論文データを生成中...")
        research = self.generate_research_data()
        with open(os.path.join(self.data_dir, "research_data.json"), "w", encoding="utf-8") as f:
            json.dump(research, f, ensure_ascii=False, indent=2)
        
        # 4. プロトコルデータ
        print("A病院プロトコル・ガイドラインを生成中...")
        protocols = self.generate_hospital_protocols()
        with open(os.path.join(self.data_dir, "hospital_protocols.json"), "w", encoding="utf-8") as f:
            json.dump(protocols, f, ensure_ascii=False, indent=2)
        
        # 5. 病院情報
        print("A病院基本情報を生成中...")
        with open(os.path.join(self.data_dir, "hospital_info.json"), "w", encoding="utf-8") as f:
            json.dump(self.hospital_info, f, ensure_ascii=False, indent=2)
        
        print("✅ A病院固有の全データ生成が完了しました！")
        print(f"データ保存先: {self.data_dir}")
        print(f"生成されたファイル:")
        print(f"- detailed_patients.json (500名の詳細患者データ)")
        print(f"- clinical_outcomes.json (A病院診療成績)")
        print(f"- research_data.json (研究・論文データ)")
        print(f"- hospital_protocols.json (A病院プロトコル)")
        print(f"- hospital_info.json (A病院基本情報)")

if __name__ == "__main__":
    generator = ComprehensiveHospitalDataGenerator()
    generator.save_all_enhanced_data()
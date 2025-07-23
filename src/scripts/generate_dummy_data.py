#!/usr/bin/env python3
"""
病院運営データのダミーデータ生成スクリプト
診療報酬分析、病床管理、事務業績などの模擬データを生成
"""

import json
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import os

fake = Faker('ja_JP')

class HospitalDataGenerator:
    def __init__(self, data_dir="src/data"):
        self.data_dir = data_dir
        self.dummy_data_dir = os.path.join(data_dir, "dummy_data")
        self.db_dir = os.path.join(data_dir, "hospital_database")
        
        # ディレクトリ作成
        os.makedirs(self.dummy_data_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)
        
        # 診療科と疾患のマスターデータ
        self.departments = [
            "内科", "外科", "整形外科", "皮膚科", "眼科", 
            "耳鼻咽喉科", "産婦人科", "小児科", "泌尿器科", "精神科"
        ]
        
        self.diseases = {
            "内科": ["高血圧", "糖尿病", "高脂血症", "心房細動", "慢性腎臓病"],
            "外科": ["胆石症", "鼠径ヘルニア", "虫垂炎", "胃がん", "大腸がん"],
            "整形外科": ["腰椎椎間板ヘルニア", "変形性膝関節症", "骨折", "肩関節周囲炎", "頸椎症"],
            "皮膚科": ["アトピー性皮膚炎", "湿疹", "蕁麻疹", "皮膚がん", "帯状疱疹"],
            "眼科": ["白内障", "緑内障", "糖尿病網膜症", "加齢黄斑変性", "結膜炎"]
        }
        
    def generate_patient_data(self, count=1000):
        """患者基本情報の生成"""
        patients = []
        
        for i in range(count):
            patient_id = f"P-{str(i+1).zfill(3)}"
            
            # 年齢に応じた疾患傾向を設定
            age = random.randint(20, 90)
            
            # アレルギー情報（約30%が何らかのアレルギー）
            allergies = []
            if random.random() < 0.3:
                allergy_list = ["ペニシリン", "セフェム系", "造影剤", "卵", "そば", "エビ・カニ"]
                allergies = random.sample(allergy_list, random.randint(1, 2))
            
            # 併用薬（年齢が高いほど多い傾向）
            current_meds = []
            if age > 50:
                med_list = ["アムロジピン", "リシノプリル", "メトホルミン", "アトルバスタチン", "オメプラゾール"]
                num_meds = min(random.randint(0, 5), int((age - 50) / 10))
                if num_meds > 0:
                    current_meds = random.sample(med_list, num_meds)
            
            # 既往歴
            conditions = []
            if age > 40 and random.random() < 0.4:
                condition_list = ["高血圧", "糖尿病", "脂質異常症", "心疾患", "腎疾患"]
                conditions = random.sample(condition_list, random.randint(1, 2))
            
            patient = {
                "id": patient_id,
                "name": fake.name(),
                "age": age,
                "gender": random.choice(["男性", "女性"]),
                "allergies": allergies,
                "current_medications": current_meds,
                "conditions": conditions,
                "insurance_type": random.choice(["国保", "社保", "後期高齢", "自費"]),
                "created_date": fake.date_between(start_date='-2y', end_date='today').isoformat()
            }
            patients.append(patient)
        
        return patients
    
    def generate_billing_data(self, patient_count=1000):
        """診療報酬データの生成（過去12ヶ月）"""
        billing_records = []
        
        # 診療行為マスター
        procedures = {
            "基本診療料": {"初診料": 282, "再診料": 73, "外来管理加算": 52},
            "検査": {"血液検査": 144, "尿検査": 27, "心電図": 130, "レントゲン": 85, "CT": 1350, "MRI": 1590},
            "処置": {"注射": 32, "点滴": 97, "処置料": 45, "リハビリ": 245},
            "手術": {"小手術": 2850, "中手術": 15600, "大手術": 58200}
        }
        
        for month_offset in range(12):
            target_date = datetime.now() - timedelta(days=30 * month_offset)
            monthly_records = []
            
            # 月間患者数（季節変動を考慮）
            base_patients = int(patient_count * 0.4)  # 月間40%の患者が受診
            seasonal_factor = 1.2 if month_offset < 3 else 0.9  # 冬季は多め
            monthly_patients = int(base_patients * seasonal_factor)
            
            for _ in range(monthly_patients):
                patient_id = f"P-{random.randint(1, patient_count):03d}"
                department = random.choice(self.departments)
                
                # 診療内容の生成
                visit_procedures = []
                total_points = 0
                
                # 基本診療料（必須）
                if random.random() < 0.7:  # 70%が再診
                    visit_procedures.append({"name": "再診料", "points": 73, "count": 1})
                    total_points += 73
                else:
                    visit_procedures.append({"name": "初診料", "points": 282, "count": 1})
                    total_points += 282
                
                # 検査
                if random.random() < 0.6:  # 60%で検査実施
                    for test_name, points in random.sample(list(procedures["検査"].items()), random.randint(1, 3)):
                        visit_procedures.append({"name": test_name, "points": points, "count": 1})
                        total_points += points
                
                # 処置
                if random.random() < 0.3:  # 30%で処置実施
                    for proc_name, points in random.sample(list(procedures["処置"].items()), 1):
                        visit_procedures.append({"name": proc_name, "points": points, "count": 1})
                        total_points += points
                
                # 査定（約5%の確率で発生）
                assessment_reduction = 0
                assessment_reason = ""
                if random.random() < 0.05:
                    assessment_reduction = random.randint(10, 100)
                    assessment_reason = random.choice([
                        "適応外使用", "重複検査", "算定要件不備", "診療録記載不備", "医学的妥当性"
                    ])
                
                record = {
                    "record_id": f"B{target_date.strftime('%Y%m')}{random.randint(10000, 99999)}",
                    "patient_id": patient_id,
                    "visit_date": target_date.strftime('%Y-%m-%d'),
                    "department": department,
                    "doctor_id": f"DR{random.randint(1, 20):02d}",
                    "procedures": visit_procedures,
                    "total_points": total_points,
                    "assessment_reduction": assessment_reduction,
                    "assessment_reason": assessment_reason,
                    "final_points": total_points - assessment_reduction,
                    "insurance_rate": 0.7 if random.random() < 0.8 else 0.9  # 80%が7割負担
                }
                
                billing_records.append(record)
        
        return billing_records
    
    def generate_bed_data(self):
        """病床管理データの生成"""
        bed_data = []
        
        # 病床構成
        bed_config = {
            "一般病床": 120,
            "ICU": 8,
            "HCU": 12,
            "回復期リハ病床": 40,
            "療養病床": 60
        }
        
        # 過去12ヶ月の病床稼働実績
        for month_offset in range(12):
            target_date = datetime.now() - timedelta(days=30 * month_offset)
            
            for bed_type, total_beds in bed_config.items():
                # 稼働率（病床タイプにより異なる）
                base_occupancy = {
                    "一般病床": 0.85,
                    "ICU": 0.75,
                    "HCU": 0.80,
                    "回復期リハ病床": 0.90,
                    "療養病床": 0.95
                }[bed_type]
                
                # 月間変動
                seasonal_factor = random.uniform(0.9, 1.1)
                monthly_occupancy = min(base_occupancy * seasonal_factor, 0.98)
                
                occupied_beds = int(total_beds * monthly_occupancy)
                
                # 平均在院日数
                avg_los = {
                    "一般病床": random.uniform(12, 16),
                    "ICU": random.uniform(3, 5),
                    "HCU": random.uniform(5, 8),
                    "回復期リハ病床": random.uniform(60, 90),
                    "療養病床": random.uniform(180, 300)
                }[bed_type]
                
                bed_record = {
                    "month": target_date.strftime('%Y-%m'),
                    "bed_type": bed_type,
                    "total_beds": total_beds,
                    "occupied_beds": occupied_beds,
                    "occupancy_rate": round(monthly_occupancy, 3),
                    "avg_length_of_stay": round(avg_los, 1),
                    "admissions": int(occupied_beds * 30 / avg_los),
                    "discharges": int(occupied_beds * 30 / avg_los * 0.95)  # 若干の差異
                }
                
                bed_data.append(bed_record)
        
        return bed_data
    
    def generate_staff_performance_data(self):
        """スタッフ業績データの生成"""
        staff_data = []
        
        departments = self.departments + ["医事課", "看護部", "薬剤部", "検査科", "放射線科"]
        
        for dept in departments:
            staff_count = random.randint(5, 25)  # 部署ごとのスタッフ数
            
            for i in range(staff_count):
                # 過去12ヶ月の個人実績
                for month_offset in range(12):
                    target_date = datetime.now() - timedelta(days=30 * month_offset)
                    
                    # 業務処理能力（個人差あり）
                    base_performance = random.uniform(0.7, 1.3)  # 個人の基本能力
                    monthly_variation = random.uniform(0.9, 1.1)  # 月間変動
                    
                    if dept in self.departments:  # 診療科の場合
                        procedures_count = int(50 * base_performance * monthly_variation)
                        revenue_per_patient = random.randint(3000, 15000)
                        patient_satisfaction = random.uniform(4.0, 5.0)
                        error_rate = random.uniform(0.001, 0.05)
                    elif dept == "医事課":
                        procedures_count = int(200 * base_performance * monthly_variation)  # 事務処理件数
                        revenue_per_patient = 0  # 直接収益なし
                        patient_satisfaction = random.uniform(3.5, 4.5)
                        error_rate = random.uniform(0.01, 0.08)
                    else:  # その他部署
                        procedures_count = int(100 * base_performance * monthly_variation)
                        revenue_per_patient = 0
                        patient_satisfaction = random.uniform(3.8, 4.8)
                        error_rate = random.uniform(0.005, 0.03)
                    
                    staff_record = {
                        "staff_id": f"{dept[:2]}{i+1:02d}",
                        "staff_name": fake.name(),
                        "department": dept,
                        "month": target_date.strftime('%Y-%m'),
                        "procedures_count": procedures_count,
                        "revenue_generated": procedures_count * revenue_per_patient if revenue_per_patient > 0 else 0,
                        "patient_satisfaction_score": round(patient_satisfaction, 1),
                        "error_rate": round(error_rate, 4),
                        "overtime_hours": random.randint(10, 50),
                        "training_hours": random.randint(2, 20)
                    }
                    
                    staff_data.append(staff_record)
        
        return staff_data
    
    def generate_hospital_kpis(self):
        """病院全体のKPIデータ生成"""
        kpi_data = []
        
        for month_offset in range(12):
            target_date = datetime.now() - timedelta(days=30 * month_offset)
            
            # 基本KPI
            monthly_revenue = random.randint(150000000, 200000000)  # 月間収益（1.5〜2億円）
            monthly_patients = random.randint(8000, 12000)
            
            kpi_record = {
                "month": target_date.strftime('%Y-%m'),
                "total_revenue": monthly_revenue,
                "total_patients": monthly_patients,
                "revenue_per_patient": int(monthly_revenue / monthly_patients),
                "bed_occupancy_rate": round(random.uniform(0.80, 0.92), 3),
                "average_los": round(random.uniform(13, 17), 1),
                "patient_satisfaction": round(random.uniform(4.0, 4.8), 1),
                "staff_satisfaction": round(random.uniform(3.5, 4.3), 1),
                "assessment_rate": round(random.uniform(0.03, 0.08), 4),
                "return_rate": round(random.uniform(0.01, 0.04), 4),
                "emergency_response_time": round(random.uniform(8, 15), 1),  # 分
                "waiting_time_outpatient": round(random.uniform(25, 45), 1)  # 分
            }
            
            kpi_data.append(kpi_record)
        
        return kpi_data
    
    def save_all_data(self):
        """全ダミーデータの生成と保存"""
        print("病院運営ダミーデータの生成を開始します...")
        
        # 1. 患者基本データ
        print("患者基本データを生成中...")
        patients = self.generate_patient_data(1000)
        with open(os.path.join(self.dummy_data_dir, "patients.json"), "w", encoding="utf-8") as f:
            json.dump({"patients": patients}, f, ensure_ascii=False, indent=2)
        
        # 2. 診療報酬データ
        print("診療報酬データを生成中...")
        billing_data = self.generate_billing_data(1000)
        with open(os.path.join(self.dummy_data_dir, "billing_records.json"), "w", encoding="utf-8") as f:
            json.dump({"billing_records": billing_data}, f, ensure_ascii=False, indent=2)
        
        # 3. 病床データ
        print("病床管理データを生成中...")
        bed_data = self.generate_bed_data()
        with open(os.path.join(self.dummy_data_dir, "bed_data.json"), "w", encoding="utf-8") as f:
            json.dump({"bed_data": bed_data}, f, ensure_ascii=False, indent=2)
        
        # 4. スタッフ実績データ
        print("スタッフ実績データを生成中...")
        staff_data = self.generate_staff_performance_data()
        with open(os.path.join(self.dummy_data_dir, "staff_performance.json"), "w", encoding="utf-8") as f:
            json.dump({"staff_performance": staff_data}, f, ensure_ascii=False, indent=2)
        
        # 5. 病院KPIデータ
        print("病院KPIデータを生成中...")
        kpi_data = self.generate_hospital_kpis()
        with open(os.path.join(self.dummy_data_dir, "hospital_kpis.json"), "w", encoding="utf-8") as f:
            json.dump({"hospital_kpis": kpi_data}, f, ensure_ascii=False, indent=2)
        
        print("✅ 全ダミーデータの生成が完了しました！")
        print(f"データ保存先: {self.dummy_data_dir}")

if __name__ == "__main__":
    generator = HospitalDataGenerator()
    generator.save_all_data()
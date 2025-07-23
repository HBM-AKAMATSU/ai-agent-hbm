# src/services/shift_scheduling_service.py (新規作成)

import json
import re
from datetime import datetime
from langchain_openai import ChatOpenAI
from config import Config
from services.n8n_connector import N8NConnector # n8n_connectorをインポート
from typing import List, Dict, Any

class ShiftSchedulingService:
    def __init__(self, n8n_connector: N8NConnector):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.3 # 創造性を持たせるため少し高め
        )
        self.n8n_connector = n8n_connector

    def generate_provisional_schedule(self, user_input: str) -> str:
        """
        ユーザーの入力からシフト希望を抽出し、仮シフトを生成してn8nに連携する。
        """
        
        # LLMにシフト希望の抽出と仮シフトの生成を依頼
        prompt = f"""
        あなたはA病院のシフト管理アシスタントです。以下のチャットメッセージから、5人分のシフト希望日と、それに基づく簡易的な仮シフト表（夜勤・日勤・休み）をJSON形式で生成してください。
        個人の希望を最大限反映しつつ、可能な限り公平に割り振ってください。

        # シフト希望の入力例（ユーザーのチャットメッセージ）:
        田中：1日、3日休み、夜勤は10日
        鈴木：2日、4日休み、日勤希望
        佐藤：夜勤固定、5日休み
        高橋：日勤固定、6日休み
        渡辺：毎日OK、休みなし

        # 生成すべきJSON形式の例:
        {{
          "schedule_date": "2025-08-01", // シフトの基準日を想定
          "shifts": [
            {{
              "name": "田中",
              "1日": "休み",
              "2日": "日勤",
              "3日": "休み",
              "4日": "日勤",
              "5日": "日勤",
              "6日": "日勤",
              "7日": "日勤",
              "8日": "日勤",
              "9日": "日勤",
              "10日": "夜勤"
            }},
            {{
              "name": "鈴木",
              "1日": "日勤",
              "2日": "休み",
              "3日": "日勤",
              "4日": "休み",
              "5日": "日勤",
              "6日": "日勤",
              "7日": "日勤",
              "8日": "日勤",
              "9日": "日勤",
              "10日": "日勤"
            }}
            // ... 他のメンバー ...
          ]
        }}
        // 注意：上記はあくまで形式の例です。実際にはメッセージから日付範囲を特定し、その日付をキーにしてください。
        // シフトの期間は柔軟に（例：入力に「来週」とあれば来週1週間分など）対応してください。
        // デモでは、直近の7日間など、固定の期間を想定しても良いでしょう。
        // 今回は簡略化のため、1日から10日までのシフトを生成してください。

        # ユーザーからのシフト希望:
        {user_input}

        # 生成するJSON:
        """
        
        try:
            # LLMからJSON形式の応答を取得
            llm_response = self.model.invoke(prompt).content
            
            # JSON形式の出力を整形（LLMが余計なテキストを付ける場合があるため）
            json_match = re.search(r'```json\n(.*?)```', llm_response, re.DOTALL)
            if json_match:
                schedule_json_str = json_match.group(1)
            else:
                schedule_json_str = llm_response # ```json```で囲まれていない場合

            schedule_data = json.loads(schedule_json_str)
            
            # n8nにデータ送信
            n8n_message = {
                "task_type": "provisional_shift_schedule",
                "schedule_data": schedule_data,
                "timestamp": datetime.now().isoformat()
            }
            n8n_response = self.n8n_connector.execute_task(json.dumps(n8n_message)) # JSON文字列として送信
            
            if "✅" in n8n_response:
                return f"シフト希望を承りました！簡易的な仮シフト表を作成し、スプレッドシートに出力しました。ご確認ください。\n{n8n_response}"
            else:
                return f"シフト表の作成に成功しましたが、スプレッドシートへの出力で問題が発生しました。\n{n8n_response}"

        except json.JSONDecodeError as e:
            return f"シフト表の生成に失敗しました。AIが正しいJSON形式を生成できませんでした。エラー: {e}\n生成されたテキスト: {llm_response}"
        except Exception as e:
            return f"シフト表の生成中にエラーが発生しました: {e}"
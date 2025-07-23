# src/main.py
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

import sys
import os
import re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.router import QuestionRouter
from services.rag_service import RAGService
from services.double_check import DoubleCheckService
from services.n8n_connector import N8NConnector
from services.billing_analysis_service import BillingAnalysisService
from services.bed_management_service import BedManagementService
from services.admin_efficiency_service import AdminEfficiencyService
from services.enhanced_clinical_analysis import EnhancedClinicalAnalysisService
from services.enhanced_double_check import EnhancedDoubleCheckService
from services.staff_training_service import StaffTrainingService
from services.conversation_manager import ConversationManager
from services.agent_service import HospitalAIAgent
from services.shift_scheduling_service import ShiftSchedulingService
from utils.report_parser import ReportParser
from langchain_openai import ChatOpenAI
import uuid

# FastAPIアプリケーションの初期化
app = FastAPI(title="Smart Hospital Work Demo")

# 各サービスのインスタンスを作成
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)
router = QuestionRouter()

# --- 変更点1: rag_serviceとweb_search_serviceを先に作成 ---
rag_service = RAGService()  # rag_serviceを先に作成
from services.web_search_service import WebSearchService
web_search_service = WebSearchService()  # web_search_serviceも先に作成
# --- ここまで変更点1 ---

n8n_connector = N8NConnector()
# 強化された患者固有対応サービス
enhanced_double_check = EnhancedDoubleCheckService()
enhanced_clinical = EnhancedClinicalAnalysisService()
# 医療事務向けサービス
billing_service = BillingAnalysisService()
bed_service = BedManagementService()
admin_service = AdminEfficiencyService()
staff_training_service = StaffTrainingService()
shift_service = ShiftSchedulingService(n8n_connector=n8n_connector)
conversation_manager = ConversationManager()

# 構造化レポート履歴の管理
structured_report_history = {}  # user_id -> {report_id: structured_data}
report_parser = ReportParser()

def store_structured_report(user_id: str, response_text: str, report_type: str = "general") -> str:
    """レポートを構造化データとして保存し、レポートIDを返す"""
    import time
    
    # レポートIDを生成（タイムスタンプベース）
    report_id = f"report_{int(time.time())}"
    
    # レポートのパース
    structured_data = report_parser.parse_report(response_text, report_type)
    
    # ユーザー別履歴の初期化
    if user_id not in structured_report_history:
        structured_report_history[user_id] = {}
    
    # 構造化データを保存
    structured_report_history[user_id][report_id] = structured_data
    
    # 古いレポートの削除（最新5つまで保持）
    user_reports = structured_report_history[user_id]
    if len(user_reports) > 5:
        oldest_key = min(user_reports.keys(), key=lambda k: int(k.split('_')[1]))
        del user_reports[oldest_key]
    
    return report_id

# --- 変更点2: HospitalAIAgent に 初期化済みサービスインスタンスを渡す ---
hospital_agent = HospitalAIAgent(rag_service=rag_service, web_search_service=web_search_service, structured_report_history=structured_report_history)
# --- ここまで変更点2 ---

# 一般的な雑談用のChatOpenAIモデル
general_chat_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=Config.OPENAI_API_KEY
)

# アプリケーション起動時に一度だけ実行される処理
@app.on_event("startup")
def startup_event():
    """アプリケーション起動時にベクトルデータベースを構築する"""
    rag_service.setup_vectorstores()
    print("AIの知識データベースの準備が完了しました。")

# LINEからのWebhook通信を受け取るエンドポイント
@app.post("/webhook")
async def callback(request: Request):
    """LINEからのリクエストを処理する"""
    try:
        # ヘッダーから署名を取得（存在しない場合のエラーハンドリング）
        signature = request.headers.get('X-Line-Signature')
        if not signature:
            print("Warning: Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # リクエストボディを取得
        body = await request.body()
        body_str = body.decode('utf-8')
        
        print(f"Received webhook request with signature: {signature[:20]}...")
        print(f"Request body length: {len(body_str)}")
        
        # LINE Bot SDKでリクエストを処理
        handler.handle(body_str, signature)
        
        print("Webhook processed successfully")
        return "OK"
        
    except InvalidSignatureError as e:
        print(f"Invalid signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"Webhook processing error: {e}")
        # デバッグ情報を出力
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

# テスト用エンドポイント
@app.get("/")
async def root():
    """アプリケーションの動作確認用エンドポイント"""
    return {
        "message": "Smart Hospital AI Enhanced is running!",
        "status": "ok",
        "version": "2.0",
        "features": [
            "A病院患者固有ダブルチェック",
            "A病院診療実績分析",
            "A病院論文研究支援",
            "A病院診療報酬分析",
            "A病院病床管理分析", 
            "A病院事務効率化分析",
            "医薬品情報検索",
            "院内規定検索"
        ],
        "hospital": "A病院（東京都中央区）",
        "patient_database": "A2024-XXXX形式 500名登録済み"
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# テキストメッセージを処理するハンドラー
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ユーザーからのテキストメッセージに応じて応答を生成する"""
    user_message = event.message.text
    reply_token = event.reply_token
    user_id = event.source.user_id  # LINEユーザーIDを取得
    response_text = ""

    # 会話履歴の確認
    has_context = conversation_manager.has_recent_conversation(user_id)
    is_follow_up = conversation_manager.is_follow_up_question(user_message) if has_context else False
    
    # 質問を分類（特定カテゴリは常に独立して分類）
    category = router.classify_question(user_message)
    
    # フォローアップ質問の特別処理（feedback, summary, double_check は除外）
    if is_follow_up and has_context and category not in ['feedback', 'summary', 'double_check', 'unknown']:
        last_category = conversation_manager.get_last_category(user_id)
        # 前回と同じカテゴリで継続する場合のみフォローアップとして扱う
        if last_category and category == last_category:
            print(f"フォローアップ質問 - カテゴリ: {category} (前回: {last_category})")
        else:
            print(f"新規質問 - カテゴリ: {category} (文脈あり)")
    else:
        if category in ['feedback', 'summary']:
            print(f"独立質問 - カテゴリ: {category}")
        else:
            print(f"新規質問 - カテゴリ: {category}")

    # 会話コンテキストを取得
    conversation_context = conversation_manager.get_conversation_context(user_id)

    # エージェントを使用すべきかどうかを判断
    use_agent = hospital_agent.should_use_agent(user_message, category)
    
    if use_agent:
        print(f"AIエージェント使用 - カテゴリ: {category}")
        response_text = hospital_agent.process_query(user_message, conversation_context, user_id)
        
        # レポート検出と構造化保存
        report_keywords = [
            "A病院 診療報酬返戻分析レポート",
            "A病院 診療報酬分析レポート", 
            "診療報酬返戻分析レポート",
            "診療報酬分析レポート"
        ]
        
        detected_report = None
        for keyword in report_keywords:
            if keyword in response_text:
                detected_report = keyword
                break
        
        if detected_report:
            try:
                # レポートのパース
                structured_data = report_parser.parse_report(response_text, "billing_analysis")
                
                # レポートIDを生成
                import time
                report_id = f"report_{int(time.time())}"
                
                # ユーザー別履歴に保存
                if user_id not in structured_report_history:
                    structured_report_history[user_id] = {}
                
                structured_report_history[user_id][report_id] = structured_data
                print(f"✅ レポート構造化保存完了: {report_id}")
                    
            except Exception as e:
                print(f"❌ レポート解析エラー: {str(e)}")
        
        # エージェントが生成した複雑な回答も構造化レポートとして保存（従来の処理）
        if len(response_text) > 200 and not detected_report:  # 専用レポート以外の長い回答
            store_structured_report(user_id, response_text, category)
    # シフト組みの処理
    elif category == "shift_scheduling":
        response_text = shift_service.generate_provisional_schedule(user_message)
    # 従来のカテゴリ別処理
    elif category == "admin":
        if conversation_context:
            response_text = rag_service.query_admin_with_history(user_message, conversation_context)
        else:
            response_text = rag_service.query_admin(user_message)
    elif category == "medical":
        if conversation_context:
            response_text = rag_service.query_medical_with_history(user_message, conversation_context)
        else:
            response_text = rag_service.query_medical(user_message)
    elif category == "summary":
        if conversation_context:
            response_text = rag_service.summarize_previous_response(conversation_context, user_message)
        else:
            response_text = """
📋 **A病院 要約機能**

申し訳ございませんが、要約する前回の会話が見つかりません。

## 💡 **要約機能の使い方**
1. まず何らかの質問をしてください（例：「80歳以上の大腿骨骨折の手術成績は？」）
2. AIからの回答を受け取ってください
3. その後「要約して」「一言でまとめると？」「ポイントは？」などと質問してください

## 🔄 **新たにご質問いただけること**
- A病院の診療実績に関するお問い合わせ
- 薬剤の安全性確認
- 患者固有のダブルチェック
- 医療事務分析

お気軽にお試しください！"""
    elif category == "double_check":
        # 基本的なダブルチェックサービス（患者名表示対応）を使用
        double_check_service = DoubleCheckService()
        response_text = double_check_service.check_medication(user_message)
    elif category == "task":
        response_text = n8n_connector.execute_task(user_message)
    # 新しい医療事務向け高度分析機能
    elif category == "billing_analysis":
        # 会話履歴を考慮した診療報酬分析
        if conversation_context:
            enhanced_query = f"# 前回までの会話内容\n{conversation_context}\n\n# 現在の質問\n{user_message}"
            response_text = billing_service.query_billing_analysis(enhanced_query)
        else:
            response_text = billing_service.query_billing_analysis(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "billing")
    elif category == "bed_management":
        # 会話履歴を考慮した病床管理分析
        if conversation_context:
            enhanced_query = f"# 前回までの会話内容\n{conversation_context}\n\n# 現在の質問\n{user_message}"
            response_text = bed_service.query_bed_management(enhanced_query)
        else:
            response_text = bed_service.query_bed_management(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "bed_management")
    elif category == "admin_efficiency":
        # 会話履歴を考慮した事務効率分析
        if conversation_context:
            enhanced_query = f"# 前回までの会話内容\n{conversation_context}\n\n# 現在の質問\n{user_message}"
            response_text = admin_service.query_admin_efficiency(enhanced_query)
        else:
            response_text = admin_service.query_admin_efficiency(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "admin_efficiency")
    elif category == "revenue_analysis":
        # 会話履歴を考慮した収益分析
        if conversation_context:
            enhanced_query = f"# 前回までの会話内容\n{conversation_context}\n\n# 現在の質問\n{user_message}"
            response_text = billing_service.analyze_revenue_performance(enhanced_query)
        else:
            response_text = billing_service.analyze_revenue_performance(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "revenue_analysis")
    elif category == "clinical_analysis":
        # 診療実績分析はRAGサービスの医療データベースを使用
        if conversation_context:
            response_text = rag_service.query_medical_with_history(user_message, conversation_context)
        else:
            response_text = rag_service.query_medical(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "clinical")
    elif category == "waiting_analysis":
        response_text = "⚠️ 待ち時間分析機能は現在開発中です。電子カルテシステムとの連携により、リアルタイム患者動線分析を提供予定です。"
    elif category == "staff_training":
        # 会話履歴を考慮したスタッフ研修分析
        if conversation_context:
            enhanced_query = f"# 前回までの会話内容\n{conversation_context}\n\n# 現在の質問\n{user_message}"
            response_text = staff_training_service.analyze_staff_training(enhanced_query)
        else:
            response_text = staff_training_service.analyze_staff_training(user_message)
        # 構造化レポートとして保存
        store_structured_report(user_id, response_text, "staff_training")
    elif category == "patient_info_query":
        # --- 修正点: 患者ID抽出の正規表現を変更 ---
        # 'A2024-0156' の形式に対応する正規表現
        patient_id_match = re.search(r'[A|a]\d{4}-\d{4}', user_message)
        # もし 'P-001' 形式もサポートしたい場合は、 OR で結合できます (例: r'([P|p]-\d{3}|[A|a]\d{4}-\d{4})')
        # 現状は 'A2024-0156' のみ対応
        # --- ここまで修正 ---
        
        patient_id = patient_id_match.group(0).upper() if patient_id_match else None

        if patient_id:
            # double_checkサービスから患者データをロード
            patient_info_data = enhanced_double_check.detailed_patients
            target_patient = patient_info_data.get(patient_id)

            if target_patient and "name" in target_patient:
                # --- 修正点: 改行コードを '\r\n' に変更 ---
                response_text = (
                    f"📋 **患者情報**\r\n\r\n"  # \n\n を \r\n\r\n に変更
                    f"患者ID: {patient_id}\r\n"   # \n を \r\n に変更
                    f"お名前: 「{target_patient['name']}」様"
                )
                # --- ここまで修正 ---
            else:
                response_text = f"申し訳ありません。患者ID {patient_id} の情報が見つからないか、お名前が登録されていません。"
        else:
            response_text = "患者IDを認識できませんでした。AXXXX-XXXX（例：A2024-0156）の形式で患者IDを教えてください。"  # エラーメッセージも修正
    elif category == "feedback":
        # ユーザーからの肯定的なフィードバックに対する応答
        import random
        feedback_responses = [
            "ありがとうございます！😊 お役に立てて嬉しいです。他にもA病院のデータについてお聞きになりたいことがございましたら、お気軽にお声がけください。",
            "そう言っていただけると幸いです！🏥 A病院の業務改善に少しでも貢献できていれば何よりです。",
            "恐縮です！💪 引き続きA病院の医療の質向上をサポートしてまいります。何か他にもご質問がございましたらどうぞ。",
            "お褒めの言葉をいただき、ありがとうございます！✨ A病院の皆様の業務効率化に貢献できるよう、今後も精進いたします。",
            "ありがとうございます！📊 A病院の診療実績や業務分析について、他にも何かお調べしたいことがございましたらお申し付けください。"
        ]
        response_text = random.choice(feedback_responses)
    elif category == "general_chat":
        # 一般的な雑談・会話処理
        chat_prompt = f"""
        あなたは友好的で、様々な話題に対応できるAIアシスタントです。
        以下のユーザーのメッセージに対して、自然で、かつ親しみやすい会話応答を生成してください。
        A病院の特定の業務に関する質問であれば、その旨を案内することもできますが、まずは一般的な会話として応答してください。

        # ユーザーのメッセージ:
        {user_message}

        # あなたの応答:
        """
        try:
            response_text = general_chat_model.invoke(chat_prompt).content
        except Exception as e:
            print(f"一般会話応答生成中にエラーが発生しました: {e}")
            response_text = "申し訳ありません、現在一般的な会話の応答を生成できません。何かA病院の業務についてお手伝いできることはありますか？"
    else:
        # AIが分類できなかった場合、より自然な案内を提供
        print(f"カテゴリ不明 ('{user_message}') のため、丁寧に案内を提供します。")
        response_text = f"""
🤖 **A病院 Smart Hospital AI**

申し訳ございません。「{user_message}」についてうまく理解できませんでした。

## 💬 **ご利用方法**
**一般的な会話**: 「こんにちは」「普通に会話はできますか？」などの雑談もお気軽にどうぞ！

**A病院の業務支援**: より具体的にお教えいただけますでしょうか？例えば：

📋 **具体的な質問例**
• 「80歳以上の大腿骨骨折の治療成績は？」
• 「患者A2024-0156の薬剤相互作用をチェックして」
• 「今月の診療報酬査定率はどうですか？」

## 💬 **ご利用いただける機能**

## 📊 **医療事務向け高度分析**
**診療報酬分析**
• 「査定率の分析をお願いします」
• 「今月の収益分析を見せて」
• 「競合他院との比較はどうですか？」

**病床管理分析** 
• 「病床稼働率を改善したい」
• 「在院日数の分析をお願いします」
• 「退院調整の効率化について」

**A病院診療実績分析**
• 「60代女性の急性心筋梗塞で、当院での治療成績は？」
• 「脳梗塞のt-PA投与例での転帰について、当院の実績は？」
• 「80歳以上の大腿骨骨折の手術成績は当院では？」

**A病院患者固有チェック**
• 「患者A2024-0156にワーファリン2mg処方したい。相互作用は？」
• 「患者A2024-0238のCT造影剤使用時のアレルギー歴確認」

**事務効率化分析**
• 「スタッフの生産性向上について」
• 「エラー率と満足度の関係を分析して」
• 「研修効果の測定をお願いします」

## 💬 **会話履歴機能**
• 「要約して」「まとめて」「ポイントは？」
• フォローアップ質問で会話が継続します

## 🏥 **基本機能**
• 薬剤情報：「ワーファリンの副作用は？」
• ダブルチェック：「P-001にワーファリンをチェックして」
• 院内規定：「有給申請の方法は？」

お気軽にお試しください！"""

    
    # 会話履歴に保存
    conversation_manager.add_message(user_id, user_message, response_text, category)
    
    # 古いセッションのクリーンアップ（定期的に実行）
    conversation_manager.cleanup_old_sessions()

    # 最終的な応答をLINEに送信
    print(f"DEBUG: 送信直前のresponse_textの内容 (repr): {repr(response_text)}")  # デバッグコード追加
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=response_text)
    )

# 画像メッセージを処理するハンドラー（今回はプレースホルダー）
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    ユーザーからの画像メッセージを処理する。
    【今後の拡張】ここで画像を取得し、n8nに送信してDriveに保存する。
    """
    # 現時点では、画像が送られてきた旨を伝えるメッセージのみを返す
    reply_token = event.reply_token
    response_text = "画像を認識しました。この画像をGoogle Driveに保存し、ダブルチェックを実行する機能は現在開発中です。"
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=response_text)
    )

if __name__ == "__main__":
    import uvicorn
    print("サーバーを起動します。 http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
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
from services.agent_service import OfficeAIAgent
from services.shift_scheduling_service import ShiftSchedulingService
from utils.report_parser import ReportParser
from langchain_openai import ChatOpenAI
import uuid

# FastAPIアプリケーションの初期化
app = FastAPI(title="Smart Office Assistant Demo")

# 各サービスのインスタンスを作成（タイムアウト設定を延長）
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN, timeout=30)  # 30秒に延長
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)
router = QuestionRouter()

# --- 変更点1: rag_serviceとweb_search_serviceを先に作成 ---
rag_service = RAGService()  # rag_serviceを先に作成
from services.web_search_service import WebSearchService
web_search_service = WebSearchService()  # web_search_serviceも先に作成
from services.email_send_service import EmailSendService
email_send_service = EmailSendService()  # メール送信サービス追加
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

def get_natural_leave_application_info():
    """LLMを使って自然な会話調の有給申請情報を生成"""
    from langchain_openai import ChatOpenAI
    from config import Config
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=Config.OPENAI_API_KEY
    )
    
    # 完全な情報を含むプロンプト
    prompt = f"""あなたは阪南ビジネスマシンの優秀で親しみやすい事務アシスタントです。
有給申請の方法について、以下の重要な情報を**必ず全て含めて**、自然で親しみやすい会話調で説明してください。

## 必須情報（必ず含めること）
1. **勤怠管理システムのURL**: https://kintaiweb.azurewebsites.net/login/login/
2. **田中さんの連絡先**: 
   - システムソリューション課の田中さん
   - 内線: 4004
   - メール: akamatsu.d@hbm-web.co.jp
   - 対応内容: パスワード再設定サポート
3. **メール送信機能**: 私から田中さんに自動でパスワードリセット依頼メールを送信可能
4. **基本的な申請手順**: ログイン→有給申請選択→日付選択→申請種別→理由→連絡先→送信→承認
5. **推奨期間**: 2週間前までの申請

## 回答スタイル
- 親しみやすく、話しかけるような自然な口調
- 「〜ですね」「〜してください」「〜していただけます」などの丁寧語
- 重要な情報は自然に強調
- 箇条書きは最小限に抑え、会話的な流れで説明

ユーザーの質問: 「有給申請の方法を教えて」

自然で親しみやすい回答:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"LLM応答生成エラー: {e}")
        # フォールバック: 基本的な情報を返す
        return """有給申請についてご説明しますね。

勤怠管理システム（https://kintaiweb.azurewebsites.net/login/login/）からお申し込みいただけます。ログイン後、メニューから「有給申請」を選択して、取得希望日や申請種別を入力していただく流れです。

もしログインでお困りの場合は、システムソリューション課の田中さん（内線4004、akamatsu.d@hbm-web.co.jp）にご相談ください。パスワードの再設定などサポートしていただけます。また、私から田中さんに自動でメールをお送りすることも可能ですので、お気軽にお申し付けください。

申請は取得予定日の2週間前までに行っていただくのがおすすめです。何かご不明な点がございましたら、いつでもお声がけくださいね。"""

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

# --- 変更点2: OfficeAIAgent に 初期化済みサービスインスタンスを渡す ---
office_agent = OfficeAIAgent(rag_service=rag_service, web_search_service=web_search_service, structured_report_history=structured_report_history)
# --- ここまで変更点2 ---

# 一般的な雑談用のChatOpenAIモデル
general_chat_model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=Config.OPENAI_API_KEY
)

# アプリケーション起動時に一度だけ実行される処理
@app.on_event("startup")
def startup_event():
    """アプリケーション起動時にベクトルデータベースを構築する"""
    rag_service.setup_vectorstores()
    print("事務作業用AIアシスタントの知識データベースの準備が完了しました。")

# LINEからのWebhook通信を受け取るエンドポイント
@app.post("/webhook")
async def callback(request: Request):
    """LINEからのリクエストを処理する"""
    try:
        print("=== Webhook request received ===")
        print(f"Headers: {dict(request.headers)}")
        
        # ヘッダーから署名を取得（存在しない場合のエラーハンドリング）
        signature = request.headers.get('X-Line-Signature')
        if not signature:
            print("Warning: Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # リクエストボディを取得
        body = await request.body()
        body_str = body.decode('utf-8')
        
        print(f"Received webhook request with signature: {signature[:20]}...")
        print(f"Body: {body_str[:200]}...")  # 最初の200文字をログ出力
        print(f"Full body: {body_str}")  # デバッグ用：全体を表示
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
        "message": "阪南ビジネスマシン Smart Office Assistant AI is running!",
        "status": "ok",
        "version": "1.0",
        "company": "阪南ビジネスマシン株式会社",
        "website": "https://hbm-web.co.jp/",
        "features": [
            "官需課売上分析",
            "担当者別実績管理",
            "メーカー別販売実績",
            "社内規定検索",
            "手続きガイド案内",
            "人事・労務サポート",
            "経費・会計処理支援",
            "営業・顧客管理支援", 
            "業務効率化分析",
            "スケジュール・予約管理",
            "文書テンプレート提供"
        ],
        "departments": [
            "官需課",
            "人事部",
            "総務部",
            "営業部"
        ],
        "current_data": "令和7年4月度合同販売会議資料対応済み",
        "sales_performance": {
            "target": "6,400万円",
            "actual": "6,740万円", 
            "achievement": "105.3%"
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# タイムアウト保護のための即座応答リスト
QUICK_RESPONSES = {
    "経費精算の締切": """📋 **経費精算の締切について**

経費精算の締切は **毎月25日** となっております。

**詳細情報**:
- 提出期限: 毎月25日 17:00まで
- 提出方法: 経費精算システムまたは総務部へ直接提出
- 遅れた場合: 翌月処理となります

詳しい手続きについては総務部までお問い合わせください。

何か他にご質問がございましたらお気軽にどうぞ！""",
    
    "達成状況": """📊 **官需課の達成状況**

7月度の官需課全体の達成状況をお調べしています。

**概要**:
- 全体達成率: 81.5%
- 主要貢献者: 高見さん、辻川さん、小濱さん
- 好調製品: XEROX/FBJ、RISO

詳細分析を準備中です。少々お待ちください..."""
}

def should_use_quick_response(user_message: str) -> str:
    """即座応答を使うべきかチェックし、該当する応答を返す"""
    
    # 経費精算の締切に関する質問
    if "経費精算" in user_message and ("締切" in user_message or "いつ" in user_message):
        return QUICK_RESPONSES["経費精算の締切"]
    
    # 達成状況に関する複雑な質問  
    if ("達成状況" in user_message or "実績" in user_message) and ("官需課" in user_message or "7月" in user_message):
        return QUICK_RESPONSES["達成状況"]
    
    return None

def should_provide_context_help(user_message: str, has_context: bool) -> str:
    """文脈不明確な質問の場合のヘルプメッセージを生成"""
    
    # フォローアップ質問でも回答できない場合
    followup_patterns = [
        "どうなりましたか", "どうなった", "結果は", "どうでしたか", 
        "どうですか", "いかがでしたか", "状況は", "進捗は"
    ]
    
    if has_context and any(pattern in user_message for pattern in followup_patterns):
        return """🔍 **前回の質問について**

申し訳ありません。前回の質問の詳細な分析結果をお調べします。

もう少し具体的に教えていただけますか？例えば：
• 「官需課全体の7月の詳細な達成状況を教えて」
• 「辻川さんの今月の売上実績は？」
• 「7月の目標達成率は何%でしたか？」

このように具体的に質問していただくと、より正確で詳しい情報をお提供できます。"""
    
    return None

# テキストメッセージを処理するハンドラー
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ユーザーからのテキストメッセージに応じて応答を生成する"""
    user_message = event.message.text
    reply_token = event.reply_token
    user_id = event.source.user_id  # LINEユーザーIDを取得
    response_text = ""
    
    # 🚀 即座応答チェック（LINEタイムアウト回避）
    quick_response = should_use_quick_response(user_message)
    if quick_response:
        print(f"⚡ 即座応答使用: '{user_message}' -> {len(quick_response)}文字")
        try:
            line_bot_api.reply_message(reply_token, TextSendMessage(text=quick_response))
            
            # 🔥 重要：即座応答でも会話履歴に保存
            conversation_manager.add_message(user_id, user_message, quick_response, "quick_response")
            print(f"✅ 即座応答の会話履歴を保存しました")
            
            return
        except Exception as e:
            print(f"❌ 即座応答送信エラー: {e}")
            # 即座応答が失敗した場合は通常処理に進む

    # 会話履歴の確認
    has_context = conversation_manager.has_recent_conversation(user_id)
    is_follow_up = conversation_manager.is_follow_up_question(user_message) if has_context else False
    
    # 🔍 デバッグ: 会話履歴の状態を確認
    print(f"🔍 DEBUG: user_id = {user_id}")
    print(f"🔍 DEBUG: has_context = {has_context}")
    print(f"🔍 DEBUG: is_follow_up = {is_follow_up}")
    print(f"🔍 DEBUG: user_message = '{user_message}'")
    
    # 🎯 文脈推測機能: 不完全な質問を補完
    enhanced_query = user_message
    was_enhanced = False
    contextual_confirmation = ""
    
    # 🔍 デバッグ: 文脈推測の条件チェック
    if has_context:
        is_incomplete = conversation_manager.is_incomplete_query(user_message)
        print(f"🔍 DEBUG: is_incomplete_query = {is_incomplete}")
        
        if is_incomplete:
            print(f"🔍 DEBUG: 文脈推測を実行します...")
            enhanced_query, was_enhanced = conversation_manager.enhance_query_with_context(user_id, user_message)
            print(f"🔍 DEBUG: enhanced_query = '{enhanced_query}'")
            print(f"🔍 DEBUG: was_enhanced = {was_enhanced}")
            
            if was_enhanced:
                contextual_confirmation = conversation_manager.generate_contextual_confirmation(user_id, user_message, enhanced_query)
                print(f"🧠 文脈推測: '{user_message}' → '{enhanced_query}'")
                print(f"🧠 確認メッセージ: '{contextual_confirmation}'")
            else:
                print(f"🔍 DEBUG: 文脈推測に失敗しました")
        else:
            print(f"🔍 DEBUG: 完全な質問として判定されました")
    else:
        print(f"🔍 DEBUG: 会話履歴なし - 文脈推測をスキップ")
    
    # 質問を分類（補完された質問を使用）
    category = router.classify_question(enhanced_query)
    
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

    # 🚨 タイムアウト対策: 文脈推測が成功した場合は簡易応答
    if was_enhanced and contextual_confirmation:
        print(f"🚀 文脈推測成功 - 簡易応答でタイムアウト回避")
        response_text = f"{contextual_confirmation}\n\n富士フィルムの複合機について詳しい情報を検索中です。少々お待ちください..."
    else:
        # エージェントを使用すべきかどうかを判断（補完された質問を使用）
        query_for_agent_check = enhanced_query if was_enhanced else user_message
        use_agent = office_agent.should_use_agent(query_for_agent_check, category)
        
        if use_agent:
            print(f"AIエージェント使用 - カテゴリ: {category}")
            # 文脈推測で補完された質問を使用
            query_to_process = enhanced_query if was_enhanced else user_message
            response_text = office_agent.process_query(query_to_process, conversation_context, user_id)
            
            # 文脈推測の確認メッセージを追加
            if was_enhanced and contextual_confirmation:
                response_text = f"{contextual_confirmation}\n\n{response_text}"
        
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
    if category == "shift_scheduling":
        response_text = shift_service.generate_provisional_schedule(user_message)
    # 従来のカテゴリ別処理
    elif category == "admin":
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        
        # 🔥 有給申請の特別処理
        if "有給" in query_to_process and "申請" in query_to_process:
            response_text = get_natural_leave_application_info()
        elif conversation_context:
            response_text = rag_service.query_office_with_history(query_to_process, conversation_context)
        else:
            # DB検索 → Web検索のフォールバック統合
            response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\n\n{response_text}"
    elif category == "sales_query":
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        if conversation_context:
            response_text = rag_service.query_sales_with_history(query_to_process, conversation_context)
        else:
            # DB検索 → Web検索のフォールバック統合
            response_text = rag_service.query_with_fallback_search(query_to_process, "sales_query")
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\n\n{response_text}"
    elif category == "detailed_sales_query":
        # 詳細営業データ専用クエリ（みなみちゃんキャラクター）
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        response_text = rag_service.query_detailed_sales(query_to_process, conversation_context)
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\n\n{response_text}"
    elif category == "report_generation":
        # レポート生成・配信処理
        from services.report_generation_service import ReportGenerationService
        from services.n8n_workflow_service import N8NWorkflowService
        
        report_service = ReportGenerationService()
        n8n_service = N8NWorkflowService()
        
        # レポートタイプの判定
        if "月次" in user_message or "monthly" in user_message.lower():
            report_content = report_service.generate_monthly_analysis()
            report_type = "monthly"
        elif "日次" in user_message or "daily" in user_message.lower():
            report_content = report_service.generate_daily_report()
            report_type = "daily"
        else:
            # カスタムレポート
            report_content = report_service.generate_custom_report(user_message)
            report_type = "custom"
        
        # 配信が要求されている場合
        if any(word in user_message for word in ["送信", "配信", "メール", "送って"]):
            # 受信者の判定
            recipient = "部長"  # デフォルト
            if "課長" in user_message:
                recipient = "課長"
            elif "チーム" in user_message or "メンバー" in user_message:
                recipient = "チーム"
            
            # N8N経由で配信
            report_data = n8n_service.format_webhook_data(report_content, report_type, recipient)
            delivery_result = n8n_service.trigger_report_email(report_data)
            
            response_text = f"""📊 **レポート生成・配信完了**

{report_content[:300]}...

📧 **配信状況**
{delivery_result}

**受信者**: {recipient}
**レポートタイプ**: {report_type}

※全文は配信メールでご確認ください。"""
        else:
            # レポートのみ生成
            response_text = report_content
    elif category == "workflow_integration":
        # シンプルなワークフロー実行メッセージ
        response_text = "✅ ワークフローを実行しました"
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
📋 **阪南ビジネスマシン 要約機能**

申し訳ございませんが、要約する前回の会話が見つかりません。

## 💡 **要約機能の使い方**
1. まず何らかの質問をしてください（例：「官需課の高見の売上実績は？」）
2. AIからの回答を受け取ってください
3. その後「要約して」「一言でまとめると？」「ポイントは？」などと質問してください

## 🔄 **新たにご質問いただけること**
- 阪南ビジネスマシンの売上実績に関するお問い合わせ
- 社内規定の確認
- 事務手続きのガイド
- 業務効率化分析

お気軽にお試しください！"""
    elif category == "double_check":
        # 基本的なダブルチェックサービス（患者名表示対応）を使用
        double_check_service = DoubleCheckService()
        response_text = double_check_service.check_medication(user_message)
    elif category == "task":
        # taskカテゴリも統合検索システム（DB → Web検索）を使用
        print(f"task カテゴリ - 統合検索を実行します。")
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        try:
            response_text = rag_service.query_with_fallback_search(query_to_process, "task")
        except Exception as e:
            print(f"task統合検索中にエラーが発生しました: {e}")
            # エラー時はN8Nコネクターにフォールバック
            response_text = n8n_connector.execute_task(query_to_process)
        
        # 文脈推測の確認メッセージを追加
        if was_enhanced and contextual_confirmation:
            response_text = f"{contextual_confirmation}\n\n{response_text}"
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
            "ありがとうございます！😊 お役に立てて嬉しいです。他にも阪南ビジネスマシンの業務についてお聞きになりたいことがございましたら、お気軽にお声がけください。",
            "そう言っていただけると幸いです！💼 阪南ビジネスマシンの業務改善に少しでも貢献できていれば何よりです。",
            "恐縮です！💪 引き続き阪南ビジネスマシンの業務効率化をサポートしてまいります。何か他にもご質問がございましたらどうぞ。",
            "お褒めの言葉をいただき、ありがとうございます！✨ 阪南ビジネスマシンの皆様の業務効率化に貢献できるよう、今後も精進いたします。",
            "ありがとうございます！📊 阪南ビジネスマシンの売上実績や業務分析について、他にも何かお調べしたいことがございましたらお申し付けください。"
        ]
        response_text = random.choice(feedback_responses)
    elif category == "general_chat":
        # 一般的な雑談・会話処理
        chat_prompt = f"""
        あなたは友好的で、様々な話題に対応できるAIアシスタントです。
        以下のユーザーのメッセージに対して、自然で、かつ親しみやすい会話応答を生成してください。
        阪南ビジネスマシンの特定の業務に関する質問であれば、その旨を案内することもできますが、まずは一般的な会話として応答してください。

        # ユーザーのメッセージ:
        {user_message}

        # あなたの応答:
        """
        try:
            response_text = general_chat_model.invoke(chat_prompt).content
        except Exception as e:
            print(f"一般会話応答生成中にエラーが発生しました: {e}")
            response_text = "申し訳ありません、現在一般的な会話の応答を生成できません。何か阪南ビジネスマシンの業務についてお手伝いできることはありますか？"
    else:
        # DBにない質問の場合、統合検索を実行（DB → Web検索）
        # 文脈推測で補完された質問を使用
        query_to_process = enhanced_query if was_enhanced else user_message
        print(f"カテゴリ不明 ('{query_to_process}') - 統合検索を実行します。")
        
        try:
            # 統合検索を実行（DB → Web検索のフォールバック）
            response_text = rag_service.query_with_fallback_search(query_to_process, "admin")
            
            # 文脈推測の確認メッセージを追加
            if was_enhanced and contextual_confirmation:
                response_text = f"{contextual_confirmation}\n\n{response_text}"
            
        except Exception as e:
            print(f"統合検索中にエラーが発生しました: {e}")
            # エラー時は従来通りの案内を表示
            response_text = f"""🤖 **阪南ビジネスマシン Smart Office Assistant**

申し訳ございません。「{query_to_process}」についてうまく理解できませんでした。

## 💬 **ご利用方法**
**一般的な会話**: 「こんにちは」「普通に会話はできますか？」などの雑談もお気軽にどうぞ！

**阪南ビジネスマシンの業務支援**: より具体的にお教えいただけますでしょうか？例えば：

📋 **具体的な質問例**
• 「官需課の高見の今期の売り上げは？」
• 「販売台数の詳細は？」
• 「有給申請の方法は？」

## 💬 **ご利用いただける機能**

## 📊 **販売実績分析**
**官需課売上分析**
• 「官需課の実績はどうですか？」
• 「担当者別の売上を教えて」
• 「メーカー別の販売状況は？」

**業績管理分析** 
• 「達成率を分析して」
• 「前年同期比はどうですか？」
• 「売上トレンドを教えて」

**阪南ビジネスマシン売上実績分析**
• 「XEROX製品の売れ行きは？」
• 「京セラ製品の販売状況は？」
• 「RISO製品の今月の実績は？」

**事務手続き支援**
• 「経費精算の方法は？」
• 「会議室の予約方法は？」
• 「備品購入の手続きは？」

**人事・労務サポート**
• 「勤怠管理の方法は？」
• 「研修制度について教えて」
• 「給与関連の質問」

## 💬 **会話履歴機能**
• 「要約して」「まとめて」「ポイントは？」
• フォローアップ質問で会話が継続します

## 🏢 **基本機能**
• 売上分析：「辻川さんの実績は？」
• 手続きガイド：「有給申請の方法は？」
• 社内規定：「経費精算のルールは？」

お気軽にお試しください！"""

    
    # === メール送信処理 ===
    # 全てのカテゴリ処理後にメール送信の必要性をチェック
    print(f"🔍 DEBUG: メール送信チェック開始")
    print(f"🔍 DEBUG: user_message = '{user_message}'")
    print(f"🔍 DEBUG: response_text長 = {len(response_text)}文字")
    
    try:
        email_sent, final_response = email_send_service.process_email_request(user_message, response_text)
        print(f"🔍 DEBUG: email_sent = {email_sent}")
        print(f"🔍 DEBUG: final_response長 = {len(final_response)}文字")
        
        if email_sent:
            print(f"📧 メール送信処理完了 - 元の回答にメール送信結果を追加")
            response_text = final_response
        else:
            print(f"📋 メール送信なし")
            # メール送信提案がある場合は追加
            if len(final_response) > len(response_text):
                print(f"💡 メール送信提案を追加")
                response_text = final_response
    except Exception as e:
        print(f"❌ メール送信処理中にエラー: {e}")
        import traceback
        traceback.print_exc()
        # メール送信エラーは回答には影響させない
    
    # 古いセッションのクリーンアップ（定期的に実行）
    conversation_manager.cleanup_old_sessions()

    # 最終的な応答をLINEに送信（再試行機能付き）
    print(f"DEBUG: 送信直前のresponse_textの内容 (repr): {repr(response_text)}")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=response_text),
                timeout=30  # 個別リクエストのタイムアウトも30秒に設定
            )
            print(f"✅ LINE応答送信成功 (試行{attempt + 1}回目)")
            
            # 🔥 重要: 送信成功後に会話履歴を保存
            conversation_manager.add_message(user_id, user_message, response_text, category)
            print(f"✅ 会話履歴保存完了: user_id={user_id}, category={category}")
            
            break
        except Exception as e:
            print(f"❌ LINE応答送信エラー (試行{attempt + 1}回目): {e}")
            if attempt == max_retries - 1:
                print(f"⚠️ 最大試行回数に達しました。応答送信を諦めます。")
            else:
                import time
                time.sleep(1)  # 1秒待ってから再試行

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
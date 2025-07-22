# src/main.py
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

from config import Config
from services.router import QuestionRouter
from services.rag_service import RAGService
from services.double_check import DoubleCheckService
from services.n8n_connector import N8NConnector

# FastAPIアプリケーションの初期化
app = FastAPI(title="Smart Hospital Work Demo")

# 各サービスのインスタンスを作成
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)
router = QuestionRouter()
rag_service = RAGService()
double_check = DoubleCheckService()
n8n_connector = N8NConnector()

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
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

# テキストメッセージを処理するハンドラー
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """ユーザーからのテキストメッセージに応じて応答を生成する"""
    user_message = event.message.text
    reply_token = event.reply_token
    response_text = ""

    # 質問を分類
    category = router.classify_question(user_message)
    print(f"質問カテゴリ: {category}") # デバッグ用にカテゴリを表示

    # カテゴリに応じた処理を実行
    if category == "admin":
        response_text = rag_service.query_admin(user_message)
    elif category == "medical":
        response_text = rag_service.query_medical(user_message)
    elif category == "double_check":
        response_text = double_check.check_medication(user_message)
    elif category == "task":
        response_text = n8n_connector.execute_task(user_message)
    else:
        # AIが分類できなかった場合、汎用的なRAGを試みる
        print("カテゴリ不明のため、事務情報と医療情報を検索します。")
        response_text = rag_service.query_admin(user_message)
        # ここでさらに応答が見つからない場合のロジックを追加することも可能

    # 最終的な応答をLINEに送信
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
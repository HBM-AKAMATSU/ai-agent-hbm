# src/config.py
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

class Config:
    # OpenAI API設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Gemini API設定（既存のものも残す）
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # LINE Bot設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    
    # N8N設定
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')  # デフォルト値を空文字に設定
    
    # Web検索API設定
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')  # Serper API（Google検索）
# test_google_api.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

print("Google API 接続テストを開始します...")

try:
    # .envファイルからAPIキーを読み込み
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("エラー: .envファイルにGEMINI_API_KEYが設定されていません。")
    else:
        print("APIキーを読み込みました。")
        genai.configure(api_key=api_key)

        # 非常に短いテキストで埋め込みを試す
        test_text = "これはAPIの接続テストです。"
        print(f"「{test_text}」の埋め込みをリクエストします...")

        result = genai.embed_content(
            model="models/text-embedding-004",
            content=test_text
        )

        # 成功すれば、結果の一部を表示
        print("✅ 成功！Google APIとの通信に成功しました。")
        # print(f"結果のベクトル（先頭5つ）: {result['embedding'][:5]}")

except Exception as e:
    print(f"❌ 失敗: テスト中にエラーが発生しました。")
    print(f"エラー内容: {e}")
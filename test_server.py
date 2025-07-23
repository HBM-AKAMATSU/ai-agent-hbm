#!/usr/bin/env python3
# 簡単なテスト用サーバー

from fastapi import FastAPI, Request
import uvicorn
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Test server is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        signature = request.headers.get('X-Line-Signature', '')
        body = await request.body()
        print(f"Received webhook request")
        print(f"Signature: {signature[:20]}...")
        print(f"Body length: {len(body)}")
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("Starting test server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
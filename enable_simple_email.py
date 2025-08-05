#!/usr/bin/env python3
# enable_simple_email.py - 簡易メール送信機能の有効化スクリプト

import os
import shutil
from datetime import datetime

def enable_simple_email():
    """簡易メール送信機能を有効化"""
    
    print("🔧 簡易メール送信機能を有効化しています...")
    
    # .envファイルのバックアップ
    env_file = ".env"
    backup_file = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if os.path.exists(env_file):
        shutil.copy(env_file, backup_file)
        print(f"✅ .envファイルを {backup_file} にバックアップしました")
    
    # .envファイルを読み込み
    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # N8N_WEBHOOK_URLを簡易メールサーバーのURLに変更
    new_lines = []
    found_n8n_line = False
    
    for line in env_content.split('\n'):
        if line.startswith('N8N_WEBHOOK_URL'):
            new_lines.append('N8N_WEBHOOK_URL=http://localhost:8001/simple-email')
            found_n8n_line = True
        else:
            new_lines.append(line)
    
    # N8N_WEBHOOK_URLが見つからない場合は追加
    if not found_n8n_line:
        new_lines.append('')
        new_lines.append('# 簡易メール送信機能（テスト用）')
        new_lines.append('N8N_WEBHOOK_URL=http://localhost:8001/simple-email')
    
    # .envファイルを更新
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ .envファイルを更新しました")
    print("📧 簡易メール送信機能が有効になりました")
    
    # 簡易メールサーバーのスクリプトを生成
    simple_email_server = """#!/usr/bin/env python3
# simple_email_server.py - 簡易メール送信サーバー

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

class SimpleEmailHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/simple-email':
            # リクエストボディを読み取り
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # JSONデータをパース
                email_data = json.loads(post_data.decode('utf-8'))
                
                # メール情報を表示
                print("\\n" + "="*50)
                print("📧 新しいメール送信リクエスト")
                print("="*50)
                print(f"宛先: {email_data.get('recipient_name', 'N/A')} ({email_data.get('recipient_email', 'N/A')})")
                print(f"件名: {email_data.get('email_subject', 'N/A')}")
                print(f"緊急度: {email_data.get('urgency', 'normal')}")
                print(f"時刻: {datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')}")
                print("-" * 50)
                print("本文:")
                print(email_data.get('email_content', 'N/A'))
                print("="*50)
                
                # 成功レスポンスを返す
                response = {
                    "status": "success",
                    "message": "📧 メール送信をシミュレートしました（ログに出力）",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except json.JSONDecodeError:
                # JSONパースエラー
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"status": "error", "message": "Invalid JSON"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                
        else:
            # 404エラー
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # アクセスログを無効化
        pass

def run_simple_email_server():
    server_address = ('localhost', 8001)
    httpd = HTTPServer(server_address, SimpleEmailHandler)
    print("🚀 簡易メールサーバーが起動しました")
    print("📍 URL: http://localhost:8001/simple-email")
    print("💡 メール送信リクエストをこのコンソールに表示します")
    print("🛑 停止するには Ctrl+C を押してください")
    print("")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 簡易メールサーバーを停止しました")
        httpd.shutdown()

if __name__ == "__main__":
    run_simple_email_server()
"""
    
    # 簡易メールサーバーファイルを作成
    with open("simple_email_server.py", 'w', encoding='utf-8') as f:
        f.write(simple_email_server)
    
    os.chmod("simple_email_server.py", 0o755)
    print("✅ 簡易メールサーバー (simple_email_server.py) を作成しました")
    
    print("\n🎯 次のステップ:")
    print("1. 新しいターミナルを開いて以下を実行:")
    print("   cd /Users/akamatsu/Desktop/ai-agent")
    print("   python3 simple_email_server.py")
    print("")
    print("2. 元のターミナルでAIサーバーを再起動:")
    print("   python3 src/main.py")
    print("")
    print("3. LINEでメール送信機能をテスト:")
    print("   「田中さんにパスワードリセットメールを送って」")
    print("")
    print("✨ メール内容がターミナルに表示されます")

if __name__ == "__main__":
    enable_simple_email()

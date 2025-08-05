#!/usr/bin/env python3
"""
データベース内容の直接確認とデバッグ
"""
import os
import sys

sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')
os.chdir('/Users/akamatsu/Desktop/ai-agent')

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def debug_database_content():
    """データベースの内容を確認"""
    print("🔍 データベース内容の詳細確認中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 事務規定データベースを読み込み
    office_db_path = "src/faiss_index_office"
    
    if not os.path.exists(office_db_path):
        print(f"❌ データベースが見つかりません: {office_db_path}")
        return False
    
    try:
        vectorstore = FAISS.load_local(office_db_path, embeddings, allow_dangerous_deserialization=True)
        print("✅ データベース読み込み成功")
        
        # 有給申請に関する検索を実行
        query = "有給申請の方法"
        results = vectorstore.similarity_search(query, k=5)
        
        print(f"\n📋 検索クエリ: '{query}'")
        print(f"📄 検索結果数: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"\n--- 結果 {i+1} ---")
            print(f"ソース: {result.metadata.get('source', 'unknown')}")
            print(f"内容: {result.page_content[:300]}...")
            
            # 重要キーワードの存在確認
            content = result.page_content
            keywords_found = []
            
            if "田中" in content:
                keywords_found.append("田中さん")
            if "内線" in content:
                keywords_found.append("内線")
            if "4004" in content:
                keywords_found.append("内線4004")
            if "tanaka@company.com" in content:
                keywords_found.append("メールアドレス")
            if "メール送信" in content:
                keywords_found.append("メール送信機能")
            if "https://kintaiweb.azurewebsites.net" in content:
                keywords_found.append("URL")
            
            if keywords_found:
                print(f"✅ 含まれる重要情報: {', '.join(keywords_found)}")
            else:
                print("❌ 重要情報が含まれていません")
        
        return True
        
    except Exception as e:
        print(f"❌ データベース読み込みエラー: {e}")
        return False

if __name__ == "__main__":
    debug_database_content()

#!/usr/bin/env python3
"""
改善された手続きデータでデータベースを再統合
"""
import os
import sys

sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')
os.chdir('/Users/akamatsu/Desktop/ai-agent')

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def update_office_database():
    """改善された手続きデータでデータベースを更新"""
    print("🔄 改善された手続きデータでデータベースを更新中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 事務規定データベース削除（再構築のため）
    import shutil
    office_db_paths = [
        "src/faiss_index_office", 
        "faiss_index_office"
    ]
    
    for path in office_db_paths:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🗑️ 既存データベースを削除: {path}")
    
    # 1. 事務規定データ読み込み
    office_docs = []
    office_docs_path = "src/data/office_docs"
    if os.path.exists(office_docs_path):
        office_loader = DirectoryLoader(
            office_docs_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        office_docs = office_loader.load()
        print(f"📁 事務規定ドキュメント: {len(office_docs)} ファイル")
    
    # 2. 手続きデータ読み込み
    procedures_docs = []
    procedures_paths = ["data/procedures", "src/data/procedures"]
    
    for path in procedures_paths:
        if os.path.exists(path):
            procedures_loader = DirectoryLoader(
                path,
                glob="*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            docs = procedures_loader.load()
            procedures_docs.extend(docs)
            print(f"📁 {path}: {len(docs)} ファイル")
    
    # 3. 全ドキュメント統合
    all_docs = office_docs + procedures_docs
    print(f"📄 総ドキュメント数: {len(all_docs)}")
    
    if not all_docs:
        print("❌ ドキュメントが見つかりません")
        return False
    
    # 4. テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(all_docs)
    print(f"📄 分割テキスト数: {len(texts)}")
    
    # 5. 新しいデータベース作成
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # 6. 保存
    vectorstore.save_local("src/faiss_index_office")
    vectorstore.save_local("faiss_index_office")
    print("✅ 統合データベースを保存しました")
    
    return True

if __name__ == "__main__":
    success = update_office_database()
    if success:
        print("\n🎉 改善されたデータベースの更新が完了しました！")
        print("💡 サーバーを再起動してテストしてください。")
        print("\n📋 期待される改善:")
        print("   - 田中さんの連絡先情報が確実に表示")
        print("   - メール送信機能の案内が含まれる")
        print("   - パスワード問題の解決方法が明記")
    else:
        print("\n❌ データベースの更新に失敗しました。")

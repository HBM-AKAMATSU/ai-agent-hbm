#!/usr/bin/env python3
"""
最終データベース統合 - 田中さんの情報を確実に含める
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

def final_database_integration():
    """最終的なデータベース統合"""
    print("🔄 最終データベース統合を実行中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 既存の事務規定データベースを削除
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
    all_documents = []
    
    # 事務規定ドキュメント
    office_docs_path = "src/data/office_docs"
    if os.path.exists(office_docs_path):
        office_loader = DirectoryLoader(
            office_docs_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        office_docs = office_loader.load()
        all_documents.extend(office_docs)
        print(f"📁 事務規定ドキュメント: {len(office_docs)} ファイル")
    
    # 2. 手続きデータ読み込み（改善版）
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
            all_documents.extend(docs)
            print(f"📁 {path}: {len(docs)} ファイル")
    
    print(f"📄 総ドキュメント数: {len(all_documents)}")
    
    if not all_documents:
        print("❌ ドキュメントが見つかりません")
        return False
    
    # 3. 手続きファイルの内容確認
    for doc in all_documents:
        if "paid_leave_procedure.txt" in doc.metadata.get("source", ""):
            print(f"📋 有給手続きファイル内容確認:")
            content_preview = doc.page_content[:300]
            print(f"   内容プレビュー: {content_preview}...")
            if "田中さん" in doc.page_content:
                print("   ✅ 田中さんの情報が含まれています")
            if "メール送信" in doc.page_content:
                print("   ✅ メール送信機能の案内が含まれています")
    
    # 4. 小さなチャンクサイズで分割（重要情報の保持）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # より小さく
        chunk_overlap=300,  # より大きなオーバーラップ
        length_function=len,
    )
    texts = text_splitter.split_documents(all_documents)
    print(f"📄 分割テキスト数: {len(texts)}")
    
    # 5. 重要チャンクの確認
    important_chunks = 0
    for i, text in enumerate(texts):
        if "田中さん" in text.page_content and "内線" in text.page_content:
            important_chunks += 1
            print(f"   ✅ チャンク {i}: 田中さんの連絡先情報を含む")
        if "メール送信" in text.page_content and "自動" in text.page_content:
            print(f"   ✅ チャンク {i}: メール送信機能の案内を含む")
    
    print(f"📧 田中さんの情報を含むチャンク数: {important_chunks}")
    
    # 6. ベクトルデータベース作成
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # 7. 保存
    vectorstore.save_local("src/faiss_index_office")
    vectorstore.save_local("faiss_index_office")
    print("✅ 最終統合データベースを保存しました")
    
    return True

if __name__ == "__main__":
    success = final_database_integration()
    if success:
        print("\n🎉 最終データベース統合が完了しました！")
        print("\n📋 改善内容:")
        print("   - 田中さんの連絡先情報が最上位に配置")
        print("   - メール送信機能が目立つ位置に配置")
        print("   - 小さなチャンクサイズで重要情報を保持")
        print("   - 基本的な質問でも詳細サポート情報を含む")
        print("\n💡 サーバーを再起動してテストしてください。")
    else:
        print("\n❌ データベースの統合に失敗しました。")

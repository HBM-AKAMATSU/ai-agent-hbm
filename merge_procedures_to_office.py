#!/usr/bin/env python3
"""
手続きデータを事務規定データベースに統合するスクリプト
ファイル書き換えなしでの解決方法
"""
import os
import sys

# 環境変数とパス設定
sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')
os.chdir('/Users/akamatsu/Desktop/ai-agent')

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def merge_procedures_to_office():
    """手続きデータを事務規定データベースに統合"""
    print("🔧 手続きデータを事務規定データベースに統合中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    
    # 既存の事務規定データベースを読み込み
    office_db_path = "src/faiss_index_office"
    if os.path.exists(office_db_path):
        print(f"📁 既存の事務規定データベースを読み込み中...")
        office_vectorstore = FAISS.load_local(office_db_path, embeddings, allow_dangerous_deserialization=True)
        print(f"✅ 事務規定データベース読み込み完了")
    else:
        print(f"❌ 事務規定データベースが見つかりません: {office_db_path}")
        return False
    
    # 手続きデータの読み込み
    procedures_paths = [
        "data/procedures",
        "src/data/procedures"
    ]
    
    all_procedures_docs = []
    
    for path in procedures_paths:
        if os.path.exists(path):
            print(f"📁 {path} から手続きデータを読み込み中...")
            loader = DirectoryLoader(
                path,
                glob="*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            docs = loader.load()
            all_procedures_docs.extend(docs)
            print(f"   -> {len(docs)} ファイルを読み込みました")
    
    if not all_procedures_docs:
        print("❌ 手続きファイルが見つかりません")
        return False
    
    print(f"📄 総手続きドキュメント数: {len(all_procedures_docs)}")
    
    # テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    procedures_texts = text_splitter.split_documents(all_procedures_docs)
    print(f"📄 分割した手続きテキスト数: {len(procedures_texts)}")
    
    # 手続きデータを事務規定データベースに追加
    procedure_vectorstore = FAISS.from_documents(procedures_texts, embeddings)
    
    # 既存のデータベースとマージ
    office_vectorstore.merge_from(procedure_vectorstore)
    print(f"🔄 手続きデータを事務規定データベースに統合しました")
    
    # 統合されたデータベースを保存
    office_vectorstore.save_local(office_db_path)
    print(f"✅ 統合データベースを保存しました: {office_db_path}")
    
    # ルートディレクトリにもコピー
    root_office_path = "faiss_index_office"
    office_vectorstore.save_local(root_office_path)
    print(f"✅ 統合データベースをコピーしました: {root_office_path}")
    
    return True

if __name__ == "__main__":
    success = merge_procedures_to_office()
    if success:
        print("\n🎉 手続きデータの事務規定データベースへの統合が完了しました！")
        print("💡 サーバーを再起動すると、adminカテゴリで新しい手続き情報が表示されます。")
        print("\n📋 期待される動作:")
        print("   「経費精算の方法を教えて」→ 毎月20日締切 + 正しいURL")
        print("   「有給申請の方法を教えて」→ 正しいURL + 田中さんの連絡先")
    else:
        print("\n❌ データベースの統合に失敗しました。")

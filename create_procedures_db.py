#!/usr/bin/env python3
"""
手続きデータベース専用作成スクリプト
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

def create_procedures_database():
    """手続きデータベースを作成"""
    print("🔧 手続きデータベースを作成中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    
    # 手続きデータの読み込み（両方のパスをチェック）
    procedures_paths = [
        "data/procedures",
        "src/data/procedures"
    ]
    
    all_documents = []
    
    for path in procedures_paths:
        if os.path.exists(path):
            print(f"📁 {path} から読み込み中...")
            loader = DirectoryLoader(
                path,
                glob="*.txt",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            docs = loader.load()
            all_documents.extend(docs)
            print(f"   -> {len(docs)} ファイルを読み込みました")
    
    if not all_documents:
        print("❌ 手続きファイルが見つかりません")
        return False
    
    print(f"📄 総ドキュメント数: {len(all_documents)}")
    
    # ドキュメント内容確認
    for i, doc in enumerate(all_documents):
        print(f"   ドキュメント {i+1}: {doc.metadata.get('source', 'Unknown')}")
        print(f"   内容プレビュー: {doc.page_content[:100]}...")
    
    # テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    texts = text_splitter.split_documents(all_documents)
    print(f"📄 分割したテキスト数: {len(texts)}")
    
    # FAISSベクトルストア作成
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # srcディレクトリに保存
    save_path = "src/faiss_index_procedures"
    vectorstore.save_local(save_path)
    print(f"✅ 手続きデータベースを保存しました: {save_path}")
    
    # ルートディレクトリにもコピー
    root_save_path = "faiss_index_procedures"
    vectorstore.save_local(root_save_path)
    print(f"✅ 手続きデータベースをコピーしました: {root_save_path}")
    
    return True

if __name__ == "__main__":
    success = create_procedures_database()
    if success:
        print("\n🎉 手続きデータベースの作成が完了しました！")
        print("💡 サーバーを再起動して新しい情報を適用してください。")
    else:
        print("\n❌ データベースの作成に失敗しました。")

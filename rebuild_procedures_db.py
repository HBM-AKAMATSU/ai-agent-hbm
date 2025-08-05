#!/usr/bin/env python3
"""
手続きデータベース再構築スクリプト
"""
import os
import sys
sys.path.append('/Users/akamatsu/Desktop/ai-agent/src')

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config

def rebuild_procedures_database():
    """手続きデータベースを再構築"""
    print("🔧 手続きデータベースを再構築中...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=Config.OPENAI_API_KEY
    )
    
    # 手続きデータの読み込み
    procedures_path = "/Users/akamatsu/Desktop/ai-agent/src/data/procedures"
    
    if not os.path.exists(procedures_path):
        print(f"❌ 手続きデータディレクトリが見つかりません: {procedures_path}")
        return False
    
    # ドキュメントローダー
    loader = DirectoryLoader(
        procedures_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    
    documents = loader.load()
    print(f"📁 読み込んだファイル数: {len(documents)}")
    
    if not documents:
        print("❌ 手続きファイルが見つかりません")
        return False
    
    # テキスト分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    texts = text_splitter.split_documents(documents)
    print(f"📄 分割したテキスト数: {len(texts)}")
    
    # FAISSベクトルストア作成
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    # 保存先パス
    save_path = "/Users/akamatsu/Desktop/ai-agent/src/faiss_index_procedures"
    
    # 古いインデックスを削除
    if os.path.exists(save_path):
        import shutil
        shutil.rmtree(save_path)
        print("🗑️ 古いインデックスを削除しました")
    
    # 新しいインデックスを保存
    vectorstore.save_local(save_path)
    print(f"✅ 手続きデータベースを保存しました: {save_path}")
    
    return True

if __name__ == "__main__":
    success = rebuild_procedures_database()
    if success:
        print("\n🎉 手続きデータベースの再構築が完了しました！")
        print("💡 サーバーを再起動して新しい情報を適用してください。")
    else:
        print("\n❌ データベースの再構築に失敗しました。")

# setup_vector_db.py (OpenAI版)
import os
import sys
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 必要なクラスをインポート
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader

def build_and_save_dbs():
    """
    ベクトルデータベースを構築し、ローカルに保存するスクリプト (OpenAI版)
    """
    print("サービスを初期化します...")
    
    # OpenAIのEmbeddingモデルを指定
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        # --- 事務規定データベースの構築 ---
        print("\n--- 事務規定データベースの構築を開始 ---")
        print("FAISS(事務)を初期化中...")
        
        loader_admin = DirectoryLoader(
            "src/data/admin_docs/", 
            glob="**/*.md", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs_admin = loader_admin.load()
        
        if docs_admin:
            text_splitter_admin = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            texts_admin = text_splitter_admin.split_documents(docs_admin)
            
            for i, doc in enumerate(texts_admin, 1):
                print(f"  -> 事務文書 {i}/{len(texts_admin)} を追加しました。")
            
            db_admin = FAISS.from_documents(texts_admin, embeddings)
            db_admin.save_local("faiss_index_admin")
            print("✅ 事務規定データベースを 'faiss_index_admin' フォルダに保存しました。")
        else:
            print("❌ 事務文書が見つかりませんでした。")

        # --- 医薬品情報データベースの構築 ---
        print("\n--- 医薬品情報データベースの構築を開始 ---")
        print("FAISS(医療)を初期化中...")
        
        loader_medical = DirectoryLoader(
            "src/data/medical_docs/", 
            glob="**/*.md", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs_medical = loader_medical.load()
        
        if docs_medical:
            text_splitter_medical = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            texts_medical = text_splitter_medical.split_documents(docs_medical)
            
            for i, doc in enumerate(texts_medical, 1):
                print(f"  -> 医療文書 {i}/{len(texts_medical)} を追加しました。")
            
            db_medical = FAISS.from_documents(texts_medical, embeddings)
            db_medical.save_local("faiss_index_medical")
            print("✅ 医薬品情報データベースを 'faiss_index_medical' フォルダに保存しました。")
        else:
            print("❌ 医療文書が見つかりませんでした。")
        
        print("\nすべての処理が完了しました。")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    build_and_save_dbs()
# setup_vector_db.py (事務作業専用秘書エージェント版)
import os
import sys
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# srcフォルダをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 必要なクラスをインポート
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader

def build_and_save_dbs():
    """
    ベクトルデータベースを構築し、ローカルに保存するスクリプト (事務作業専用版)
    """
    print("事務作業専用AIアシスタントのデータベースを構築します...")
    
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # 作業ディレクトリをスクリプトの場所に変更
    
    # OpenAIのEmbeddingモデルを指定
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    try:
        # --- 販売会議資料データベースの構築 ---
        print("\n--- 販売会議資料データベースの構築を開始 ---")
        print("FAISS(販売会議資料)を初期化中...")
        
        # 販売会議資料データを読み込み
        sales_data_path = "data/sales_meeting_data.txt"
        if os.path.exists(sales_data_path):
            loader_sales = TextLoader(sales_data_path, encoding='utf-8')
            docs_sales = loader_sales.load()
            
            text_splitter_sales = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            texts_sales = text_splitter_sales.split_documents(docs_sales)
            
            for i, doc in enumerate(texts_sales, 1):
                print(f"  -> 販売会議資料 チャンク {i}/{len(texts_sales)} を追加しました。")
            
            db_sales = FAISS.from_documents(texts_sales, embeddings)
            db_sales.save_local("faiss_index_sales")
            print("✅ 販売会議資料データベースを 'faiss_index_sales' フォルダに保存しました。")
        else:
            print("❌ 販売会議資料データが見つかりませんでした。")

        # --- 事務規定データベースの構築 ---
        print("\n--- 事務規定データベースの構築を開始 ---")
        print("FAISS(事務規定)を初期化中...")
        
        loader_office = DirectoryLoader(
            "src/data/office_docs/", 
            glob="**/*.md", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs_office = loader_office.load()
        
        if docs_office:
            text_splitter_office = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            texts_office = text_splitter_office.split_documents(docs_office)
            
            for i, doc in enumerate(texts_office, 1):
                print(f"  -> 事務規定文書 {i}/{len(texts_office)} を追加しました。")
            
            db_office = FAISS.from_documents(texts_office, embeddings)
            db_office.save_local("faiss_index_office")
            print("✅ 事務規定データベースを 'faiss_index_office' フォルダに保存しました。")
        else:
            print("❌ 事務規定文書が見つかりませんでした。")

        # --- 手続きガイドデータベースの構築 ---
        print("\n--- 手続きガイドデータベースの構築を開始 ---")
        print("FAISS(手続きガイド)を初期化中...")
        
        # Markdownファイルを読み込み
        loader_procedures_md = DirectoryLoader(
            "src/data/procedures_docs/", 
            glob="**/*.md", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs_procedures_md = loader_procedures_md.load()
        
        # テキストファイルも読み込み
        loader_procedures_txt = DirectoryLoader(
            "data/procedures/", 
            glob="**/*.txt", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        docs_procedures_txt = loader_procedures_txt.load()
        
        # 両方のドキュメントを結合
        docs_procedures = docs_procedures_md + docs_procedures_txt
        
        if docs_procedures:
            text_splitter_procedures = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            texts_procedures = text_splitter_procedures.split_documents(docs_procedures)
            
            for i, doc in enumerate(texts_procedures, 1):
                print(f"  -> 手続きガイド文書 {i}/{len(texts_procedures)} を追加しました。")
            
            db_procedures = FAISS.from_documents(texts_procedures, embeddings)
            db_procedures.save_local("faiss_index_procedures")
            print("✅ 手続きガイドデータベースを 'faiss_index_procedures' フォルダに保存しました。")
        else:
            print("❌ 手続きガイド文書が見つかりませんでした。")
        
        print("\n🎉 事務作業専用AIアシスタントのデータベース構築が完了しました！")
        print("\n📋 構築されたデータベース:")
        print("  - faiss_index_sales (販売会議資料)")
        print("  - faiss_index_office (事務規定)")
        print("  - faiss_index_procedures (手続きガイド - MD & TXTファイル含む)")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    build_and_save_dbs()
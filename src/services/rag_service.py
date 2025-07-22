# src/services/rag_service.py (OpenAI版 - import修正)
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from config import Config

class RAGService:
    def __init__(self):
        self.model = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.admin_vectorstore = None
        self.medical_vectorstore = None
    
    # setup_vectorstoresは以前の「読み込み専用」のままでOKです
    def setup_vectorstores(self):
        """保存されたベクトルデータベースを読み込む"""
        print("保存されたベクトルデータベースを読み込みます...")
        try:
            if os.path.exists("faiss_index_admin"):
                self.admin_vectorstore = FAISS.load_local(
                    "faiss_index_admin", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("事務規定データベースの読み込み完了。")
            else:
                print("警告: 保存された事務DB 'faiss_index_admin' が見つかりません。")

            if os.path.exists("faiss_index_medical"):
                self.medical_vectorstore = FAISS.load_local(
                    "faiss_index_medical", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("医薬品情報データベースの読み込み完了。")
            else:
                print("警告: 保存された医療DB 'faiss_index_medical' が見つかりません。")
        except Exception as e:
            print(f"データベースの読み込み中にエラーが発生しました: {e}")

    def _generate_response(self, question: str, vectorstore, prompt_template: str) -> str:
        if not vectorstore:
            return "申し訳ありません、関連するデータベースが初期化されていません。"
        
        docs = vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=question)
        
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"回答生成中にエラーが発生しました: {e}")
            return "申し訳ありません、回答を生成できませんでした。"

    def query_admin(self, question: str) -> str:
        prompt_template = """
        あなたはA病院の事務規定に詳しいアシスタントです。以下の参考文書を基に、職員からの質問に親切かつ正確に回答してください。
        
        # 参考文書:
        {context}
        
        # 質問:
        {question}
        
        # 回答:
        """
        return self._generate_response(question, self.admin_vectorstore, prompt_template)

    def query_medical(self, question: str) -> str:
        prompt_template = """
        あなたはA病院の薬剤情報に精通した医療専門家です。以下の医薬品情報を基に、医療従事者からの質問に専門的かつ正確に回答してください。
        
        # 参考文書:
        {context}
        
        # 質問:
        {question}
        
        # 回答:
        """
        return self._generate_response(question, self.medical_vectorstore, prompt_template)
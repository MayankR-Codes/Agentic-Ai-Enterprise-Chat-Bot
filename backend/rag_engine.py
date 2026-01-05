from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

VECTOR_DB_PATH = "vector_store/faiss_index"

def build_vector_db(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

    vector_db = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vector_db.save_local(VECTOR_DB_PATH)

def load_vector_db():
    embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

    return FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)

if __name__ == "__main__":
    pdf_path = "data/Annual-Report-2024-25.pdf"
    build_vector_db(pdf_path)
    print("✅ Vector database created successfully.")

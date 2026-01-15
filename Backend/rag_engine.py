import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Determine absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store", "faiss_index")
DATA_DIR = os.path.join(BASE_DIR, "data")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# -------------------- BUILD VECTOR DB --------------------
def build_vector_db(pdf_path: str):
    print("📄 Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print("✂️ Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,        # ✅ ideal for dense PDFs
        chunk_overlap=80,      # ✅ preserves context
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    # 🧠 Add metadata for better grounding
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(pdf_path)
        chunk.metadata["page"] = chunk.metadata.get("page", "N/A")

    print(f"🔢 Total chunks created: {len(chunks)}")

    print("🧠 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}  # ✅ IMPORTANT
    )

    print("📦 Building FAISS index...")
    vector_db = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vector_db.save_local(VECTOR_DB_PATH)

    print("✅ Vector database created successfully.")


# -------------------- LOAD VECTOR DB --------------------
def load_vector_db():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )

    return FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    pdf_path = os.path.join(DATA_DIR, "Annual-Report-2024-25.pdf")
    build_vector_db(pdf_path)

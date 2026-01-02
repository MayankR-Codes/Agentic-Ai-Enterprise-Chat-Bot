import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# -------- LangChain (Modern & Stable) --------
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA


# -------- Your RAG Engine --------
from backend.rag_engine import load_vector_db


# -------- Streamlit Page Config --------
st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Enterprise RAG Assistant")
st.caption("Ask questions from your internal company documents")

# -------- Initialize LLM (Gemini) --------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

# -------- Load Vector DB --------
@st.cache_resource
def load_db():
    return load_vector_db()

vector_db = load_db()

# -------- RAG Chain --------
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True
)

# -------- UI --------
user_query = st.text_input(
    "Ask a question about the company report:",
    placeholder="e.g. What was the total revenue in 2024?"
)

if st.button("Ask"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            result = qa_chain.invoke({"query": user_query})

        st.subheader("Answer")
        st.write(result["result"])

        with st.expander("Source Documents"):
            for i, doc in enumerate(result["source_documents"], start=1):
                st.markdown(f"**Source {i}:**")
                st.write(doc.page_content[:800] + "...")

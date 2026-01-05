import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# -------- LangChain Imports --------
from langchain_google_genai import ChatGoogleGenerativeAI

# -------- Your Backend --------
from backend.agent import get_agent, detect_issue
from backend.rag_engine import load_vector_db
from backend.tools import get_all_tickets, get_all_meetings

# -------- Streamlit Page Config --------
st.set_page_config(
    page_title="HCLTech Enterprise Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .issue-box {background-color: #ffcccc; padding: 10px; border-radius: 5px;}
    .success-box {background-color: #ccffcc; padding: 10px; border-radius: 5px;}
    .info-box {background-color: #ccccff; padding: 10px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 HCLTech Enterprise Assistant")
st.caption("Your AI-powered companion for queries, issues, and HR requests")

# -------- Sidebar Configuration --------
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.radio(
        "Select Mode:",
        ["Chat Assistant", "Issue Manager", "Knowledge Base"],
        help="Choose how you want to interact with the assistant"
    )
    
    user_name = st.text_input("Your Name:", placeholder="John Doe")
    user_email = st.text_input("Your Email:", placeholder="john@hcltech.com")
    
    st.divider()
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.success("✅ Chat history cleared")
    
    st.divider()
    
    # Display recent tickets/meetings
    if st.checkbox("📊 Show Dashboard"):
        tabs = st.tabs(["Tickets", "Meetings"])
        
        with tabs[0]:
            tickets = get_all_tickets()
            if tickets:
                st.dataframe(
                    {
                        "Ticket ID": [t["ticket_id"] for t in tickets],
                        "Issue": [t["issue"][:50] for t in tickets],
                        "Status": [t["status"] for t in tickets],
                        "Created": [t["created_at"][:10] for t in tickets]
                    }
                )
            else:
                st.info("No tickets yet")
        
        with tabs[1]:
            meetings = get_all_meetings()
            if meetings:
                st.dataframe(
                    {
                        "Meeting ID": [m["meeting_id"] for m in meetings],
                        "Department": [m["department"] for m in meetings],
                        "Status": [m["status"] for m in meetings],
                        "Date": [m["date"] for m in meetings]
                    }
                )
            else:
                st.info("No meeting requests yet")

# -------- Initialize Session State --------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("⏳ Loading agent..."):
        try:
            st.session_state.agent = get_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.error(f"❌ Failed to load agent: {e}")
            st.session_state.agent_ready = False

# -------- Main Chat Interface --------
if not st.session_state.agent_ready:
    st.error("⚠️ Agent is not ready. Please check your configuration.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------- User Input --------
user_input = st.chat_input(
    "Ask me anything... (query, issue, or meeting request)",
    key="user_input"
)

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Process with agent
    with st.chat_message("assistant"):
        with st.spinner("🤔 Processing..."):
            try:
                # Detect if it's an issue
                issue_check = detect_issue(user_input)
                
                # Route based on mode
                if mode == "Chat Assistant":
                    # Use full agent with all tools
                    response = st.session_state.agent.invoke(
                        {"input": user_input},
                        return_intermediate_steps=False
                    )
                    
                    assistant_response = response.get("output", "I couldn't process your request.")
                    
                    # Show issue detection result
                    if issue_check.get("requires_action"):
                        st.markdown(f"""
                        <div class="issue-box">
                        🚨 <strong>Issue Detected:</strong> {issue_check.get('category', 'general')}
                        </div>
                        """, unsafe_allow_html=True)
                
                elif mode == "Issue Manager":
                    # Only use action tools
                    if issue_check.get("requires_action"):
                        response = st.session_state.agent.invoke(
                            {"input": user_input},
                            return_intermediate_steps=False
                        )
                        assistant_response = response.get("output", "Issue processing failed.")
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ {assistant_response}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        assistant_response = "This doesn't appear to be an issue. Please use 'Chat Assistant' mode for general queries."
                        st.markdown(f"""
                        <div class="info-box">
                        ℹ️ {assistant_response}
                        </div>
                        """, unsafe_allow_html=True)
                
                elif mode == "Knowledge Base":
                    # Only use RAG knowledge base
                    try:
                        vector_db = load_vector_db()
                        docs = vector_db.similarity_search(user_input, k=3)
                        
                        if docs:
                            assistant_response = f"**Found {len(docs)} relevant documents:**\n\n"
                            for i, doc in enumerate(docs, 1):
                                assistant_response += f"**Document {i}:**\n{doc.page_content[:500]}...\n\n"
                        else:
                            assistant_response = "No relevant documents found in the knowledge base."
                        
                        st.markdown(assistant_response)
                    except Exception as e:
                        assistant_response = f"❌ Knowledge base search failed: {e}"
                        st.markdown(assistant_response)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
            
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# -------- Footer --------
st.divider()
st.caption("🔒 All interactions are logged for audit purposes. User information required for issue tracking.")


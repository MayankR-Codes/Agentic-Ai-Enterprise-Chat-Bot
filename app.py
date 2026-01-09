import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# -------------------- ENV --------------------
load_dotenv()

# -------------------- BACKEND --------------------
from Backend.agent import get_agent
from Backend.tools import get_all_tickets, get_all_meetings

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="HCLTech Enterprise Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- STYLING --------------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .chat-box {
        padding: 15px;
        border-radius: 8px;
        margin-top: 8px;
        border-left: 5px solid #ccc;
    }
    
    .issue-box {
        background-color: #ffe6e6;
        border-left: 5px solid #ff4d4d;
    }
    
    .success-box {
        background-color: #e6ffe6;
        border-left: 5px solid #2ecc71;
    }
    
    .info-box {
        background-color: #eef2ff;
        border-left: 5px solid #4c6ef5;
    }
    
    .meeting-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #667eea;
        margin-bottom: 10px;
    }
    
    .ticket-card {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("""
<div class="main-header">
    <h1>🤖 HCLTech Enterprise Assistant</h1>
    <p>AI-Powered Chat, Issue Management & Meeting Scheduler</p>
</div>
""", unsafe_allow_html=True)

# -------------------- TABS --------------------
tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📋 All Meetings", "🎫 All Tickets"])

# ==================== TAB 1: CHAT ASSISTANT ====================
with tab1:
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        st.subheader("Chat with Agent")
        
        # -------- SESSION STATE --------
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "agent" not in st.session_state:
            with st.spinner("🚀 Initializing enterprise agent..."):
                st.session_state.agent = get_agent()
        
        # -------- CHAT HISTORY --------
        chat_container = st.container(height=500, border=True)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"], unsafe_allow_html=True)
        
        # -------- INPUT --------
        col_input, col_clear = st.columns([4, 1])
        with col_input:
            user_input = st.chat_input(
                "Ask anything... (query, issue, or meeting request)",
                key="chat_input"
            )
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        # -------- PROCESS INPUT --------
        if user_input:
            # Display user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Processing..."):
                    try:
                        result = st.session_state.agent.invoke(user_input)
                        response_text = result.get("output", "No response received.")
                        
                        # Color code response
                        lower = response_text.lower()
                        if "issue" in lower or "proceed" in lower or "yes" in lower or "no" in lower:
                            css = "issue-box"
                        elif "created" in lower or "submitted" in lower or "cancelled" in lower or "meeting" in lower:
                            css = "success-box"
                        else:
                            css = "info-box"
                        
                        st.markdown(
                            f"<div class='chat-box {css}'>{response_text}</div>",
                            unsafe_allow_html=True
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text
                        })
                        st.rerun()
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)[:200]}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    with col2:
        st.subheader("Quick Actions")
        
        st.markdown("**Example Queries:**")
        if st.button("📊 What was the revenue?"):
            st.session_state.messages.append({"role": "user", "content": "What was the revenue in 2024?"})
            st.rerun()
        
        if st.button("⚠️ System is broken"):
            st.session_state.messages.append({"role": "user", "content": "The login system is broken"})
            st.rerun()
        
        if st.button("👥 Meet HR"):
            st.session_state.messages.append({"role": "user", "content": "I need to meet with HR"})
            st.rerun()
        
        if st.button("📋 Policies?"):
            st.session_state.messages.append({"role": "user", "content": "What are the company policies?"})
            st.rerun()
        
        st.divider()
        st.markdown("**Stats:**")
        
        # Helper call to get fresh data
        tickets = get_all_tickets()
        meetings = get_all_meetings()
        
        st.metric("Total Messages", len(st.session_state.messages))
        st.metric("Meetings Created", len(meetings))
        st.metric("Tickets Created", len(tickets))

# ==================== TAB 2: ALL MEETINGS ====================
with tab2:
    st.subheader("📅 HR Meetings Created")
    
    meetings_data = get_all_meetings()
    
    if meetings_data:
        # Display as cards
        for meeting in meetings_data:
            st.markdown(f"""
<div class="meeting-card">
    <h4>{meeting['meeting_id']} - {meeting['department']}</h4>
    <p><b>Reason:</b> {meeting['reason']}</p>
    <p><b>Status:</b> {meeting['status']}</p>
    <p><b>Requester:</b> {meeting['user_name']}</p>
    <p><b>Created:</b> {meeting['created_at'][:19]}</p>
</div>
            """, unsafe_allow_html=True)
        
        # Display as table
        st.divider()
        st.subheader("Table View")
        df_meetings = pd.DataFrame(meetings_data)
        st.dataframe(
            df_meetings[['meeting_id', 'department', 'reason', 'status', 'created_at']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export
        csv = df_meetings.to_csv(index=False)
        st.download_button(
            label="📥 Download Meetings CSV",
            data=csv,
            file_name="meetings.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No meetings created yet. Start chatting to create one!")

# ==================== TAB 3: ALL TICKETS ====================
with tab3:
    st.subheader("🎫 IT Support Tickets Created")
    
    tickets_data = get_all_tickets()
    
    if tickets_data:
        # Display as cards
        for ticket in tickets_data:
            st.markdown(f"""
<div class="ticket-card">
    <h4>{ticket['ticket_id']} - {ticket['status']}</h4>
    <p><b>Issue:</b> {ticket['issue']}</p>
    <p><b>Priority:</b> {ticket['priority']}</p>
    <p><b>Assigned to:</b> {ticket['assigned_to']}</p>
    <p><b>Created:</b> {ticket['created_at'][:19]}</p>
</div>
            """, unsafe_allow_html=True)
        
        # Display as table
        st.divider()
        st.subheader("Table View")
        df_tickets = pd.DataFrame(tickets_data)
        st.dataframe(
            df_tickets[['ticket_id', 'issue', 'priority', 'status', 'created_at']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export
        csv = df_tickets.to_csv(index=False)
        st.download_button(
            label="📥 Download Tickets CSV",
            data=csv,
            file_name="tickets.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No tickets created yet. Start chatting to create one!")

# -------------------- FOOTER --------------------
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    <p>🔒 <b>HCLTech Enterprise Assistant</b> | Powered by AI | Secure & Scalable</p>
    <p>Chat → Issue Detection → Action Creation (Meetings & Tickets)</p>
</div>
""", unsafe_allow_html=True)

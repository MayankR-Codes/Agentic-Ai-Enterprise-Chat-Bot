import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# -------------------- ENV --------------------
load_dotenv()

# -------------------- BACKEND --------------------
from Backend.agent import get_agent
from Backend.tools import get_all_tickets, get_all_meetings
from Backend.auth import login_user, create_user, get_user_by_username

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="HCLTech Enterprise Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SESSION STATE INIT --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "notifications_enabled" not in st.session_state:
    st.session_state.notifications_enabled = True
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def notify_status_change():
    if st.session_state.notifications_enabled:
        st.toast("✅ System notifications enabled")
    else:
        st.toast("🔕 Notifications silenced")

def dark_mode_feedback():
    if st.session_state.dark_mode:
        st.toast("🌙 Dark Mode Activated")
    else:
        st.toast("☀️ Light Mode Activated")

# -------------------- GLOBAL SIDEBAR CONTROLS --------------------
with st.sidebar:
    # 1. User Profile (If logged in)
    if st.session_state.get('logged_in', False):
        user = st.session_state.user
        initials = user['full_name'][:2] if user and user['full_name'] else "U"
        username_display = user['full_name'] if user and user['full_name'] else "User"

        st.markdown(f"""
        <div class="sidebar-user">
            <div style="width: 40px; height: 40px; background: #6366f1; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">
                {initials.upper()}
            </div>
            <div>
                <div style="font-weight: 600; color: var(--text-primary);">{username_display}</div>
                <div class="sidebar-status">● Online</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

    # 2. System Control (Always visible)
    st.markdown("### System Control")
    st.toggle("Notifications", key="notifications_enabled", on_change=notify_status_change)
    st.toggle("Dark Mode", key="dark_mode", on_change=dark_mode_feedback)
    st.divider()

# -------------------- SESSION RECOVERY --------------------
# Check for session token in URL if not already logged in
if "user" in st.query_params and not st.session_state.logged_in:
    token_username = st.query_params["user"]
    user_info = get_user_by_username(token_username)
    if user_info:
        st.session_state.logged_in = True
        st.session_state.user = user_info
# -------------------- STYLING --------------------
# -------------------- STYLING --------------------
bg_primary = "#111827" if st.session_state.dark_mode else "#f8f9fa"
bg_card = "#1f2937" if st.session_state.dark_mode else "white"
text_primary = "#f9fafb" if st.session_state.dark_mode else "#111827"
text_secondary = "#d1d5db" if st.session_state.dark_mode else "#4b5563"
border_color = "#374151" if st.session_state.dark_mode else "#e5e7eb"
bubble_user = "#4338ca" if st.session_state.dark_mode else "#e0e7ff"
bubble_user_text = "white" if st.session_state.dark_mode else "#1e1b4b"
bubble_assistant = "#1f2937" if st.session_state.dark_mode else "#ffffff"
bubble_assistant_text = "#f9fafb" if st.session_state.dark_mode else "#374151"
auth_card_bg = "rgba(17, 24, 39, 0.95)" if st.session_state.dark_mode else "rgba(255, 255, 255, 0.95)"
input_bg = "#1f2937" if st.session_state.dark_mode else "#f9fafb"

# Theme Configuration
if st.session_state.get('dark_mode', False):
    # Dark Mode Palette
    primary = "#6366f1"
    primary_dark = "#4f46e5"
    accent = "#f87171"
    bg_gradient = "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)"
    card_bg = "rgba(30, 41, 59, 0.8)"
    text_main = "#f8fafc"
    text_muted = "#94a3b8"
    border = "rgba(255, 255, 255, 0.1)"
    input_bg = "rgba(15, 23, 42, 0.6)"
else:
    # Light/SaaS Palette
    primary = "#4f46e5"
    primary_dark = "#4338ca"
    accent = "#ef4444"
    bg_gradient = "linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)"
    card_bg = "rgba(255, 255, 255, 0.75)"
    text_main = "#1f2937"
    text_muted = "#6b7280"
    border = "#e5e7eb"
    input_bg = "rgba(255, 255, 255, 0.6)"

st.markdown(f"""
<style>
    :root {{
        --primary: {primary};
        --primary-dark: {primary_dark};
        --accent: {accent};
        --bg-gradient: {bg_gradient};
        --card-bg: {card_bg};
        --text-main: {text_main};
        --text-muted: {text_muted};
        --border: {border};
        --input-bg: {input_bg};
        
        /* Aliases for compatibility */
        --text-primary: {text_main};
        --text-secondary: {text_muted};
        --border-color: {border};
        --bg-card: {card_bg};
        --bg-primary: {primary};
        --bubble-user: {primary};
        --bubble-user-text: #ffffff;
        --radius-lg: 12px;
        --radius-xl: 24px;
    }}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Global Body/Background */
    .stApp {{
        background: var(--bg-gradient);
        font-family: 'Inter', sans-serif;
    }}

    /* Fix icon rendering issues (ligatures appearing as text) */
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Outlined');
    
    .material-icons, .material-icons-outlined {{
        font-family: 'Material Icons' !important;
        speak: none;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
    }}

    /* GLOBAL FIX: Force hide the keyboard icon text if font fails */
    body :not(script):not(style) {{
        text-indent: 0;
    }}

    /* Sidebar Toggle Button - Premium Blue Circle */
    [data-testid="stSidebarCollapseButton"] {{
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        z-index: 999999 !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    [data-testid="stSidebarCollapseButton"]:hover {{
        background-color: #1d4ed8 !important;
        transform: scale(1.1) !important;
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.4) !important;
    }}

    /* Hide default Streamlit icons and text in the button */
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] .material-icons {{
        display: none !important;
        opacity: 0 !important;
        font-size: 0 !important;
    }}

    /* Inject Hamburger Symbol */
    [data-testid="stSidebarCollapseButton"]::before {{
        content: "☰" !important;
        color: white !important;
        font-size: 24px !important;
        line-height: 44px !important;
        display: block !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        pointer-events: none !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border) !important;
    }}

    .auth-card {{
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--radius-xl);
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }}

    /* Pulse Logo Animation */
    .logo-container {{
        text-align: center;
        margin-bottom: 30px;
    }}
    
    .logo-pulse {{
        width: 64px;
        height: 64px;
        background: var(--primary);
        color: white;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        margin: 0 auto 15px;
        animation: pulse 2.5s infinite ease-in-out;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.5); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 15px rgba(79, 70, 229, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }}
    }}

    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 2px solid var(--border);
        gap: 0;
        margin-bottom: 25px;
    }}

    .stTabs [data-baseweb="tab"] {{
        flex: 1;
        transition: all 0.3s;
        border: none !important;
        background: transparent !important;
        padding: 12px !important;
        height: 50px !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }}

    /* Input Field Styling */
    .stTextInput input {{
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        height: 52px !important;
        padding-left: 15px !important;
        font-size: 1rem !important;
        transition: all 0.3s !important;
    }}

    .stTextInput input:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
        background-color: white !important;
    }}

    /* Primary Button */
    div.stButton > button[kind="primary"] {{
        background-color: var(--primary) !important;
        color: white !important;
        border-radius: var(--radius-lg) !important;
        height: 52px !important;
        width: 100% !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        transition: all 0.3s !important;
        margin-top: 10px !important;
    }}

    div.stButton > button[kind="primary"]:hover {{
        background-color: var(--primary-dark) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4) !important;
    }}

    /* Social Dividers */
    .divider {{
        display: flex;
        align-items: center;
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 20px 0;
    }}

    .divider::before, .divider::after {{
        content: '';
        flex: 1;
        border-bottom: 1px solid var(--border);
    }}

    .divider span {{
        padding: 0 12px;
    }}

    /* Social Login Buttons */
    .social-container {{
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }}

    .social-btn {{
        flex: 1;
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        color: var(--text-main);
    }}

    .social-btn:hover {{
        background: #f9fafb;
        border-color: #d1d5db;
        transform: translateY(-1px);
    }}

    .social-btn img {{
        width: 18px;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-main) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }}

    p, span, label, li {{
        color: var(--text-muted) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Chat Bubbles */
    .chat-bubble {{
        padding: 12px 18px;
        border-radius: 18px;
        max-width: 80%;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}

    .user-bubble {{
        background: var(--primary) !important;
        color: white !important;
        border-bottom-right-radius: 4px;
    }}

    .assistant-bubble {{
        background: var(--card-bg) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border) !important;
        border-bottom-left-radius: 4px;
    }}

    .footer-text {{
        text-align: center;
        margin-top: 30px;
        font-size: 0.85rem;
    }}

</style>

<script>
    // Ultimate fix for the "keyboard_double_arrow" issue
    function applyHamburgerFix() {{
        // 1. Target the button specifically
        const toggleBtn = document.querySelector('[data-testid="stSidebarCollapseButton"]');
        if (toggleBtn && !toggleBtn.hasAttribute('data-cleaned')) {{
            // Clean it out
            toggleBtn.innerHTML = '';
            
            // Re-inject the symbol safely
            const icon = document.createElement('div');
            icon.innerHTML = '☰';
            icon.style.cssText = 'color:white; font-size:24px; pointer-events:none;';
            toggleBtn.appendChild(icon);
            toggleBtn.setAttribute('data-cleaned', 'true');
        }}

        // 2. Global scan for the problematic string
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while(node = walker.nextNode()) {{
            if (node.textContent.includes('keyboard_double_arrow')) {{
                const parent = node.parentElement;
                if (parent) {{
                    parent.style.display = 'none';
                    parent.style.opacity = '0';
                    parent.style.fontSize = '0';
                }}
            }}
        }}

        // 3. Keep the button blue and visible
        if (toggleBtn) {{
            toggleBtn.style.backgroundColor = '#2563eb';
            toggleBtn.style.display = 'flex';
            toggleBtn.style.visibility = 'visible';
            toggleBtn.style.opacity = '1';
        }}
    }}

    // Run aggressively
    applyHamburgerFix();
    setInterval(applyHamburgerFix, 100);
    
    const observer = new MutationObserver(applyHamburgerFix);
    observer.observe(document.body, {{ childList: true, subtree: true, characterData: true }});
</script>
""", unsafe_allow_html=True)


# =========================================================
#                    AUTHENTICATION FLOW
# =========================================================
if not st.session_state.logged_in:
    # Responsive and Centered Layout
    col1, col2, col3 = st.columns([1, 1.25, 1])
    
    with col1:
        # Placeholder for potential left-side content/illustration
        pass

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start of Card Container
        with st.container():
            st.markdown("""
            <div class="auth-card">
                <div class="logo-container">
                    <h1 style="color: var(--text-main); font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px;">Welcome Back</h1>
                    <div style="font-size: 4rem; margin: 15px 0;">🤖</div>
                    <p style="color: var(--text-muted); font-size: 1rem;">Sign in to your Enterprise Workspace</p>
                </div>
            """, unsafe_allow_html=True)
            
            auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])

            with auth_tab1:
                st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="e.g. john.doe")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                    
                    if submit_login:
                        result = login_user(username, password)
                        if result["success"]:
                            st.session_state.logged_in = True
                            st.session_state.user = result["user"]
                            # Persist session in URL
                            st.query_params["user"] = result["user"]["username"]
                            if st.session_state.notifications_enabled:
                                st.toast("✅ Signed in successfully!")
                            st.rerun()
                        else:
                            if st.session_state.notifications_enabled:
                                st.error(f"❌ {result['message']}")
                

            with auth_tab2:
                st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
                with st.form("register_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_user = st.text_input("Username", placeholder="john.doe")
                    with c2:
                        full_name = st.text_input("Full Name", placeholder="John Doe")
                    
                    email = st.text_input("Email", placeholder="john@hcltech.ac.in")
                    new_pass = st.text_input("Password", type="password", placeholder="Min. 8 characters")
                    new_confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                    
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    submit_register = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                    
                    if submit_register:
                        import re
                        email_pattern = r"^[a-zA-Z0-9._%+-]+@hcltech\.ac\.in$"
                        
                        if not new_user or not new_pass or not full_name or not email or not new_confirm_pass:
                             st.warning("⚠️ Please fill in all required fields.")
                        elif new_pass != new_confirm_pass:
                             st.error("❌ Passwords do not match. Please try again.")
                        elif not re.match(email_pattern, email):
                             if st.session_state.notifications_enabled:
                                 st.error("❌ Email must be a valid @hcltech.ac.in address.")
                        else:
                            result = create_user(new_user, new_pass, full_name, email)
                            if result["success"]:
                                if st.session_state.notifications_enabled:
                                    st.success("✅ Account created! Please log in.")
                            else:
                                if st.session_state.notifications_enabled:
                                    st.error(f"❌ {result['message']}")
            
            st.markdown("</div>", unsafe_allow_html=True) # End of .auth-card
            
        st.markdown("""
        <div class="footer-text">
            <p>Protected by Enterprise Grade Security</p>
            <p style="opacity: 0.7;">© 2026 HCLTech • ModernSaaS v2.5</p>
        </div>
        """, unsafe_allow_html=True)

    # Stop execution here if not logged in
    st.stop()


# =========================================================
#                    HELPER FUNCTIONS
# =========================================================

@st.dialog("📅 Meeting Details")
def show_meeting_details(meeting):
    st.markdown(f"<h3 style='color:var(--text-primary);'>{meeting['department']} Department</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--text-secondary);'><b>Meeting ID:</b> <code style='color:var(--text-main); background:var(--input-bg);'>{meeting['meeting_id']}</code></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid var(--border-color); margin: 15px 0;'>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<p style='color:var(--text-primary);'><b>Date:</b> {meeting['date']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-primary);'><b>Time:</b> {meeting['time']}</p>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<p style='color:var(--text-primary);'><b>Status:</b> <span style='color:#10b981; font-weight:bold;'>{meeting['status']}</span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-primary);'><b>Created:</b> {meeting['created_at'][:10]}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border-top: 1px solid var(--border-color); margin: 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-primary); font-weight:bold;'>Reason for Meeting:</p>", unsafe_allow_html=True)
    st.info(meeting['reason'])
    
    st.markdown("<p style='color:var(--text-primary); font-weight:bold; margin-top:20px;'>Requested By:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--text-secondary); font-size:0.9rem;'>{meeting['user_name']} ({meeting['user_email']})</p>", unsafe_allow_html=True)
    
    if st.button("Close Dialog", use_container_width=True):
        st.rerun()

# =========================================================
#                    MAIN APPLICATION
# =========================================================

# -------------------- HEADER --------------------
st.markdown("""
<div class="main-header">
    <h1>🤖 HCLTech Enterprise Assistant</h1>
    <p>AI-Powered Support • Instant Issue Resolution • Smart Scheduling</p>
</div>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        # Clear persistent session from URL
        st.query_params.clear()
        st.rerun()
    
    if st.session_state.get('notifications_enabled', True):
        st.info("System Version 2.5.0\n\nConnected to Enterprise LLM v2")

    st.divider()
    st.markdown("### 📥 Data Reports")
    
    all_tickets = get_all_tickets()
    all_meetings = get_all_meetings()
    
    if all_tickets:
        st.download_button(
            label="📄 Export All Tickets (CSV)",
            data=pd.DataFrame(all_tickets).to_csv(index=False),
            file_name=f"all_tickets_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="sidebar_export_tickets"
        )
        
    if all_meetings:
        st.download_button(
            label="📅 Export All Meetings (CSV)",
            data=pd.DataFrame(all_meetings).to_csv(index=False),
            file_name=f"all_meetings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="sidebar_export_meetings"
        )

# -------------------- TABS --------------------
tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📅 Meetings", "🎫 Support Tickets"])

# ==================== TAB 1: CHAT ASSISTANT ====================
with tab1:
    col1, col2 = st.columns([2.5, 1], gap="large")
    
    with col1:
        st.subheader(f"👋 Hi, {username_display}!")
        
        # -------- SESSION STATE --------
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "agent" not in st.session_state:
            with st.spinner("🚀 Initializing secure enterprise environment..."):
                st.session_state.agent = get_agent()
        
        # -------- CHAT AREA --------
        # Using a container with a custom height for better UX
        chat_container = st.container(height=600, border=False)
        
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <h3 style="color: var(--text-primary);">How can I help you today?</h3>
                    <p>I can help you schedule meetings, report IT issues, or answer company queries.</p>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.messages:
                # Custom HTML rendering for messages to use our fancy CSS
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                        <div class="chat-bubble user-bubble">
                            {msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Parse specific keywords for styling internal alerts
                    content = msg["content"]
                    extra_class = ""
                    icon = ""
                    if "issue" in content.lower() or "sorry" in content.lower():
                        extra_class = "status-warning"
                        icon = "⚠️"
                    elif "schedule" in content.lower() or "created" in content.lower() or "confirmed" in content.lower():
                        extra_class = "status-success"
                        icon = "✅"
                    else:
                        extra_class = "status-info"
                        icon = "ℹ️"

                    # If it's a standard simple response, just use bubble, otherwise add status box look
                    if len(content) < 150 and (icon != "ℹ️"):
                         st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                            <div class="chat-bubble assistant-bubble" style="background: var(--card-bg); border: 1px solid var(--border-color);">
                                <div class="{extra_class}" style="margin:0; border:none; background:transparent; padding:0;">
                                    <span style="font-size: 1.2rem;">{icon}</span> {content}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                            <div class="chat-bubble assistant-bubble">
                                {content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        
        # -------- INPUT --------
        st.markdown("###") # Spacer
        col_input, col_clear = st.columns([5, 1])
        with col_input:
            user_input = st.chat_input(
                "Type your request here...",
                key="chat_input"
            )
        with col_clear:
            if st.button("Clear", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()
        
        # -------- PROCESS INPUT --------
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.rerun() # Rerun to show user message immediately styling

    # Handle agent response separately to allow streaming feeling (or just processing state)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with col1:
            with st.spinner("⚡ Thinking..."):
                try:
                    last_user_msg = st.session_state.messages[-1]["content"]
                    result = st.session_state.agent.invoke(last_user_msg)
                    response_text = result.get("output", "I apologize, but I couldn't process that request.")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
                    st.rerun()
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.rerun()

    
    with col2:
        st.subheader("💡 Quick Actions")
        
        action_btn_style = """
        <style>
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            font-weight: 500;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            border-color: #4f46e5;
            color: #4f46e5 !important;
            background-color: var(--bg-primary);
        }
        </style>
        """
        st.markdown(action_btn_style, unsafe_allow_html=True)
        
        if st.button("📊 Financial Summary"):
            st.session_state.messages.append({"role": "user", "content": "What was the revenue in 2024?"})
            st.rerun()
        
        if st.button("⚠️ Report System Issue"):
            st.session_state.messages.append({"role": "user", "content": "I need to report a login failure"})
            st.rerun()
        
        if st.button("📅 Schedule HR Meeting"):
            st.session_state.messages.append({"role": "user", "content": "Schedule a meeting with HR for performance review"})
            st.rerun()
        
        if st.button("📜 Company Policies"):
            st.session_state.messages.append({"role": "user", "content": "Summarize the remote work policy"})
            st.rerun()
        
        st.divider()
        st.caption("Live System Stats")
        
        tickets = get_all_tickets()
        meetings = get_all_meetings()
        
        c1, c2 = st.columns(2)
        c1.metric("Messages", len(st.session_state.messages))
        c2.metric("Actions", len(tickets) + len(meetings))
        
        if st.session_state.get('notifications_enabled', True):
            st.info(f"Connected to Enterprise Knowledge Base\n\nLast Sync: {datetime.now().strftime('%H:%M')}")

# ==================== TAB 2: MEETINGS ====================
with tab2:
    meetings_data = get_all_meetings()
    
    if meetings_data:
        col_header, col_export = st.columns([3, 1])
        with col_header:
            st.subheader("📅 Meeting Scheduler Dashboard")
        with col_export:
            st.download_button(
                label="📥 Download CSV",
                data=pd.DataFrame(meetings_data).to_csv(index=False),
                file_name="meetings_export.csv",
                mime="text/csv",
                use_container_width=True,
                key="tab_export_meetings"
            )
        
        for meeting in meetings_data[::-1]:
            # Create a card container
            with st.container():
                st.markdown(f"""
                <div class="card" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <h4 style="color:var(--text-primary); margin-bottom:0;">{meeting['department']} Department</h4>
                            <p style="color:var(--text-secondary); margin-top:5px;">{meeting['reason']}</p>
                            <span class="tag tag-blue">{meeting['meeting_id']}</span>
                            <span class="tag tag-green">{meeting['status']}</span>
                        </div>
                        <div style="text-align:right; font-size:0.85rem; color:var(--text-secondary);">
                            <p style="margin:0;">{meeting['created_at'][:10]}</p>
                            <p style="margin:0;">{meeting['created_at'][11:16]}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Use st.columns to put the user info and button in the same row
                card_footer = st.container()
                with card_footer:
                    # CSS-like styling for the bottom part of the card
                    st.markdown("""
                    <div style="background:var(--bg-card); padding: 0px 24px 20px 24px; border: 1px solid var(--border-color); border-top: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;">
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; gap:8px; margin-top: 10px;">
                            <div style="width:24px; height:24px; background:var(--bubble-user); border-radius:50%; display:flex; align-items:center; justify-content:center; color:var(--bubble-user-text); font-size:12px; font-weight:bold;">
                                {meeting['user_name'][0]}
                            </div>
                            <span style="font-size:0.9rem; color:var(--text-primary);">{meeting['user_name']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        if st.button("View Details →", key=f"btn_{meeting['meeting_id']}", use_container_width=True):
                            show_meeting_details(meeting)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:50px;">
            <h3>No meetings scheduled</h3>
            <p style="color:var(--text-secondary);">Use the chat assistant to book your first meeting.</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 3: TICKETS ====================
with tab3:
    tickets_data = get_all_tickets()
    
    if tickets_data:
        col_header, col_export = st.columns([3, 1])
        with col_header:
            st.subheader("🎫 IT Support Dashboard")
        with col_export:
            st.download_button(
                label="📥 Download CSV",
                data=pd.DataFrame(tickets_data).to_csv(index=False),
                file_name="tickets_export.csv",
                mime="text/csv",
                use_container_width=True,
                key="tab_export_tickets"
            )
        
        priority_colors = {
            "High": "tag-orange",
            "Medium": "tag-blue",
            "Low": "tag-green"
        }
        
        # Grid layout for tickets
        cols = st.columns(2)
        
        for idx, ticket in enumerate(tickets_data):
            # Alternate columns
            with cols[idx % 2]:
                tag_class = priority_colors.get(ticket.get('priority', 'Medium'), 'tag-blue')
                
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <h4 style="color:var(--text-primary); margin-bottom:0;">{ticket['ticket_id']}</h4>
                        <span class="tag {tag_class}">{ticket['priority']} Priority</span>
                    </div>
                    <p style="margin-top:10px; font-weight:500; color:var(--text-primary);">{ticket['issue']}</p>
                    <p style="font-size:0.9rem; color:var(--text-secondary);">Assigned to: <b style="color:var(--text-primary);">{ticket['assigned_to']}</b></p>
                    
                    <div style="margin-top:15px; padding-top:15px; border-top:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.85rem; color:var(--text-secondary);">{ticket['status']}</span>
                        <span style="font-size:0.85rem; color:var(--text-secondary);">{ticket['created_at'][:10]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:50px;">
            <h3>All systems operational</h3>
            <p style="color:var(--text-secondary);">No open support tickets found.</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------- FOOTER --------------------
st.markdown("""
<div class="footer">
    <p><b>HCLTech Enterprise Assistant</b> &copy; 2026</p>
    <p style="font-size: 0.9rem;">Secured by Agentic AI • Version 2.4.0</p>
</div>
""", unsafe_allow_html=True)
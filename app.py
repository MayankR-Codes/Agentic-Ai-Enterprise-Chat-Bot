import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import time
import textwrap
import os

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
if "notification_history" not in st.session_state:
    st.session_state.notification_history = []
if "browser_notifications_allowed" not in st.session_state:
    st.session_state.browser_notifications_allowed = False
if "pending_alerts" not in st.session_state:
    st.session_state.pending_alerts = []
if "show_activity_log" not in st.session_state:
    st.session_state.show_activity_log = False

def add_notification(message, type="info"):
    """Centralized notification handler (Toast + History + Browser Push)"""
    # 1. Add to History
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.notification_history.insert(0, {
        "message": message,
        "time": timestamp,
        "type": type
    })
    
    # Keep history manageable
    if len(st.session_state.notification_history) > 50:
        st.session_state.notification_history.pop()

    # 2. Show Toast (if enabled)
    if st.session_state.get('notifications_enabled', True):
        if type == "success":
            st.toast(f"✅ {message}")
        elif type == "error":
            st.toast(f"❌ {message}")
        elif type == "warning":
            st.toast(f"⚠️ {message}")
        else:
            st.toast(f"ℹ️ {message}")

    # 3. Add to Browser Alert Queue (if allowed)
    if st.session_state.get('browser_notifications_allowed', False):
        st.session_state.pending_alerts.append({"message": message, "type": type})

def notify_status_change():
    if st.session_state.notifications_enabled:
        add_notification("System notifications enabled", type="success")
    else:
        st.toast("🔕 Notifications silenced") # Don't add to log if muted? Actually, maybe we should.

# -------------------- SESSION RECOVERY --------------------
# Check for session token in URL if not already logged in
if "user" in st.query_params and not st.session_state.logged_in:
    token_username = st.query_params["user"]
    user_info = get_user_by_username(token_username)
    if user_info:
        st.session_state.logged_in = True
        st.session_state.user = user_info

# -------------------- USER CONTEXT --------------------
username_display = "User"
initials = "U"
if st.session_state.logged_in and st.session_state.user:
    user = st.session_state.user
    initials = user['full_name'][:2] if user.get('full_name') else "U"
    username_display = user['full_name'] if user.get('full_name') else "User"

# -------------------- GLOBAL SIDEBAR CONTROLS --------------------
with st.sidebar:
    # 1. User Profile (If logged in)
    if st.session_state.get('logged_in', False):
        st.markdown(f"""
        <div class="sidebar-user-profile">
            <div class="profile-avatar">{initials.upper()}</div>
            <div class="profile-info">
                <div class="profile-name">{username_display}</div>
                <div class="profile-status">
                    <span class="status-dot"></span>
                    <span>Online</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Log Out Button (Right below profile)
        if st.button("Log Out", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.query_params.clear()
            add_notification("Successfully signed out.", type="info")
            st.rerun()
        
        st.divider()

        # 2. Activity Log
        log_label = f"Activity Log {'▼' if st.session_state.show_activity_log else '▶'}"
        if st.button(log_label, use_container_width=True, key="activity_log_toggle"):
            st.session_state.show_activity_log = not st.session_state.show_activity_log
            st.rerun()

        if st.session_state.show_activity_log:
            with st.container():
                st.markdown("<div class='activity-log-container'>", unsafe_allow_html=True)
                if not st.session_state.notification_history:
                    st.info("No notifications recorded yet.")
                else:
                    for note in st.session_state.notification_history:
                        color = "#10b981" if note["type"] == "success" else "#3b82f6"
                        if note["type"] == "error": color = "#ef4444"
                        if note["type"] == "warning": color = "#f59e0b"
                        
                        item_html = f"<div style='border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 10px; font-size: 0.85rem;'>" \
                                    f"<span style='color: var(--text-muted); font-size: 0.75rem;'>{note['time']}</span><br>" \
                                    f"<span style='color: var(--text-main); font-size: 0.85rem;'>{note['message']}</span></div>"
                        st.markdown(item_html, unsafe_allow_html=True)
                    if st.button("Clear History", use_container_width=True):
                        st.session_state.notification_history = []
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📥 Data Reports")
        
        all_tickets = get_all_tickets()
        all_meetings = get_all_meetings()
        
        if all_tickets:
            st.download_button(
                label="📄 Export All Tickets (JSON)",
                data=pd.DataFrame(all_tickets).to_json(orient="records", indent=4),
                file_name=f"all_tickets_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
                key="sidebar_export_tickets"
            )
            
        if all_meetings:
            st.download_button(
                label="📅 Export All Meetings (JSON)",
                data=pd.DataFrame(all_meetings).to_json(orient="records", indent=4),
                file_name=f"all_meetings_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
                key="sidebar_export_meetings"
            )
        
        # Live System Stats
        st.divider()
        st.markdown("### 📊 History")
        c1, c2 = st.columns(2)
        c1.metric("Messages", len(st.session_state.get("messages", [])))
        c2.metric("Actions", len(all_tickets) + len(all_meetings))
        
        st.divider()
        
        # Footer with System Version (Last in sidebar)
        st.markdown("""
        <div style='text-align: center; padding: 16px 0; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 16px;'>
            <p style='font-size: 0.85rem; color: var(--text-muted); margin: 4px 0;'><b>HCLTech Enterprise Assistant</b> © 2026</p>
            <p style='font-size: 0.8rem; color: var(--text-muted); margin: 4px 0;'>Secured by Agentic AI • Version 2.4.0</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------- STYLING --------------------
# Dark Mode Only (Always Active)
bg_primary = "#111827"
bg_card = "#1f2937"
text_primary = "#f9fafb"
text_secondary = "#d1d5db"
border_color = "#374151"
bubble_user = "#4338ca"
bubble_user_text = "white"
bubble_assistant = "#1f2937"
bubble_assistant_text = "#f9fafb"
auth_card_bg = "rgba(17, 24, 39, 0.95)"
input_bg = "#1f2937"

# Dark Mode Palette Only
primary = "#6366f1"
primary_dark = "#4f46e5"
accent = "#f87171"
bg_gradient = "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)"
card_bg = "rgba(30, 41, 59, 0.8)"
text_main = "#f8fafc"
text_muted = "#94a3b8"
border = "rgba(255, 255, 255, 0.3)"
input_bg_dark = "rgba(15, 23, 42, 0.6)"

st.markdown("""
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
        opacity: 1 !important;
        visibility: visible !important;
    }}

    /* Also target the header button only if it's the chevron expand button */
    header[data-testid="stHeader"] button:first-of-type:not([data-testid="stStatusWidget"]) {{
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
        position: relative !important;
        margin-left: 10px !important;
        z-index: 999999 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}

    [data-testid="stSidebarCollapseButton"]:hover,
    header[data-testid="stHeader"] button:first-of-type:hover {{
        background-color: #1d4ed8 !important;
        transform: scale(1.1) !important;
        box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.4) !important;
    }}

    /* Hide default Streamlit icons and text in both buttons */
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] .material-icons,
    header[data-testid="stHeader"] button:first-of-type svg,
    header[data-testid="stHeader"] button:first-of-type span {{
        display: none !important;
        opacity: 0 !important;
        font-size: 0 !important;
    }}

    /* Inject Hamburger Symbol into both */
    [data-testid="stSidebarCollapseButton"]::before,
    header[data-testid="stHeader"] button:first-of-type::before {{
        content: "☰" !important;
        color: white !important;
        font-size: 24px !important;
        line-height: normal !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        pointer-events: none !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border) !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: var(--border) !important;
        opacity: 1 !important;
        margin: 1.5rem 0 !important;
    }}

    /* Enhanced Sidebar User Profile */
    .sidebar-user-profile {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 0;
    }}

    .profile-avatar {{
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border-radius: 50%;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.8rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        flex-shrink: 0;
    }}

    .profile-info {{
        display: flex;
        flex-direction: column;
        gap: 6px;
    }}

    .profile-name {{
        font-weight: 700;
        color: var(--text-main);
        font-size: 1.1rem;
    }}

    .profile-status {{
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--text-muted);
        font-size: 0.9rem;
    }}

    .status-dot {{
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 2s infinite;
    }}

    @keyframes pulse-dot {{
        0%, 100% {{
            opacity: 1;
            transform: scale(1);
        }}
        50% {{
            opacity: 0.5;
            transform: scale(1.1);
        }}
    }}

    /* Log Out Button - Red Styling */
    div[data-testid="stSidebar"] button[key="logout_btn"] {{
        background-color: #ef4444 !important;
        color: white !important;
        border: 1px solid #dc2626 !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }}

    div[data-testid="stSidebar"] button[key="logout_btn"]:hover {{
        background-color: #dc2626 !important;
        border-color: #b91c1c !important;
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
        color: var(--text-main) !important;
    }}

    .stTextInput input:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
        background-color: white !important;
        color: var(--text-main) !important;
    }}
    
    /* Chat Input Styling */
    .stChatInputContainer input {{
        color: var(--text-main) !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
    }}
    
    .stChatInputContainer input::placeholder {{
        color: var(--text-muted) !important;
    }}

    /* Primary Buttons - Using Native Streamlit Styling */

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

    /* Style the Activity Log Container when expanded */
    .activity-log-container {{
        padding: 15px;
        background-color: rgba(0, 0, 0, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-top: none;
        border-radius: 0 0 8px 8px;
        margin-top: -1px;
    }}

    /* Ensure the toggle button looks like a bottom-aligned part of the control group */
    div[data-testid="stSidebar"] button[key="activity_log_toggle"] {{
        justify-content: space-between !important;
    }}

    /* Target the text nodes specifically if possible, but CSS can't. JS will handle text nodes. */

    /* Card Component */
    .card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 5px solid var(--border);
        position: relative;
        overflow: hidden;
    }}

    .card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: var(--primary);
    }}

    /* Priority Indicators */
    .priority-high {{ border-left-color: #ef4444 !important; }}
    .priority-medium {{ border-left-color: #f59e0b !important; }}
    .priority-low {{ border-left-color: #3b82f6 !important; }}

    /* Tag Component */
    .tag {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        line-height: 1;
    }}

    .tag-blue {{ background: rgba(59, 130, 246, 0.15) !important; color: #3b82f6 !important; border: 1px solid rgba(59, 130, 246, 0.3) !important; }}
    .tag-green {{ background: rgba(34, 197, 94, 0.15) !important; color: #22c55e !important; border: 1px solid rgba(34, 197, 94, 0.3) !important; }}
    .tag-red {{ background: rgba(239, 68, 68, 0.15) !important; color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.3) !important; }}
    .tag-orange {{ background: rgba(245, 158, 11, 0.15) !important; color: #f59e0b !important; border: 1px solid rgba(245, 158, 11, 0.3) !important; }}

    /* Sidebar Buttons - Using Native Streamlit Styling */

    .footer-text {{
        text-align: center;
        margin-top: 30px;
        font-size: 0.85rem;
    }}

    /* Hide "Press Enter to submit form" hint */
    [data-testid="InputInstructions"] {{
        display: none !important;
    }}

</style>

<script>
    // Robust fix for the "keyboard_double_arrow" and "expand_more" ligature leak
    function applyHamburgerFix() {{
        // Target buttons specifically to keep them clean
        const buttons = document.querySelectorAll('[data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] button');
        buttons.forEach(btn => {{
            if (!btn.hasAttribute('data-cleaned')) {{
                // Hide all children text/icons
                Array.from(btn.children).forEach(child => child.style.display = 'none');
                btn.setAttribute('data-cleaned', 'true');
            }}
        }});

        // Target Sidebar Expanders and Popovers specifically to remove "expand_more" text
        const dropdownButtons = document.querySelectorAll('div[data-testid="stSidebar"] [data-testid="stExpander"] summary, div[data-testid="stSidebar"] [data-testid="stPopover"] > button');
        dropdownButtons.forEach(btn => {{
            // Find leaked text nodes inside the button
            const walker = document.createTreeWalker(btn, NodeFilter.SHOW_TEXT, null, false);
            let node;
            while(node = walker.nextNode()) {{
                if (node.textContent.includes('expand_more')) {{
                    node.textContent = node.textContent.replace('expand_more', '');
                }}
            }}
        }});

        // Global scan for leaked Material Icon text
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while(node = walker.nextNode()) {{
            const text = node.textContent.trim();
            if (text === 'keyboard_double_arrow_right' || 
                text === 'keyboard_double_arrow_left' || 
                text === 'keyboard_arrow_right' || 
                text === 'keyboard_arrow_left' || 
                text === 'expand_more') {{
                node.textContent = '';
                const parent = node.parentElement;
                // Don't hide the whole parent if it's the popover button itself, just clear the text
                if (parent && parent.tagName === 'BUTTON' && parent.closest('[data-testid="stPopover"]')) {{
                     node.textContent = '';
                }} else if (parent && !parent.closest('.stChatFloatingInputContainer')) {{
                    parent.style.display = 'none';
                    parent.style.opacity = '0';
                    parent.style.fontSize = '0';
                }}
            }}
        }}
    }}

    // Initial fix and periodic check to handle dynamic rendering
    applyHamburgerFix();
    setInterval(applyHamburgerFix, 150);
    
    // Observer for faster reaction to DOM changes
    const observer = new MutationObserver(applyHamburgerFix);
    observer.observe(document.body, {{ childList: true, subtree: true }});
</script>
""".format(
    primary=primary,
    primary_dark=primary_dark,
    accent=accent,
    bg_gradient=bg_gradient,
    card_bg=card_bg,
    text_main=text_main,
    text_muted=text_muted,
    border=border,
    input_bg=input_bg
), unsafe_allow_html=True)


# =========================================================
#                    AUTHENTICATION FLOW
# =========================================================
if not st.session_state.logged_in:
    # Apply dark theme styling for auth page
    auth_theme = """
    <style>
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
        }
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        .auth-container {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .auth-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            border-radius: 20px;
            padding: 48px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .auth-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .auth-header h1 {
            color: #f1f5f9;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 20px 0 10px 0;
            letter-spacing: -1px;
        }
        .auth-header p {
            color: #cbd5e1;
            font-size: 1rem;
            margin: 0;
        }
        .auth-logo {
            font-size: 5rem;
            margin: 20px 0;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: transparent;
            border-bottom: 2px solid rgba(100, 116, 139, 0.3);
        }
        .stTabs [aria-selected="true"] {
            color: #ef4444 !important;
            border-bottom: 3px solid #ef4444 !important;
        }
        .stTabs [aria-selected="false"] {
            color: #94a3b8 !important;
        }
        .stTextInput > div > div > input,
        .stTextInput input {
            background: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid rgba(100, 116, 139, 0.3) !important;
            color: #f1f5f9 !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
        }
        .stTextInput > div > div > input::placeholder,
        .stTextInput input::placeholder {
            color: #64748b !important;
        }
        .stTextInput > div > div > input:focus,
        .stTextInput input:focus {
            background: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid #ef4444 !important;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
            color: #64748b !important;
        }
        .stTextInput > div > div > input:active,
        .stTextInput input:active {
            color: #64748b !important;
        }
        /* Auth Page Buttons - Using Native Streamlit Styling */
        .auth-footer {
            text-align: center;
            margin-top: 40px;
            color: #64748b;
            font-size: 0.85rem;
        }
        .auth-footer p {
            margin: 4px 0;
        }
        
        /* Mobile Responsive - Stack Layout */
        @media (max-width: 768px) {
            /* Hide desktop columns and stack vertically */
            [data-testid="column"] {
                width: 100% !important;
            }
            
            /* Ensure footer moves to bottom on mobile */
            .auth-footer {
                position: fixed;
                bottom: 20px;
                left: 0;
                right: 0;
                width: 100%;
                padding: 0 20px;
                background: linear-gradient(to top, rgba(15, 23, 42, 0.95), transparent);
                z-index: 100;
            }
            
            /* Add bottom margin to auth content to avoid overlap with footer */
            .auth-card {
                margin-bottom: 120px;
            }
        }
    </style>
    """
    st.markdown(auth_theme, unsafe_allow_html=True)
    
    # Side-by-side layout
    col_left, col_right = st.columns(2)
    
    # LEFT SIDE - Welcome Card
    with col_left:
        st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
        col_img_left, col_img_center, col_img_right = st.columns([0.2, 3, 1.5])
        with col_img_center:
            st.image("assests/HCLTech_idqK8D3W3f_1.png", use_container_width=True)
        
        # Footer
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        footer_html = """
        <div class="auth-footer" style="padding-right: 150px;">
            <p>🔒 Protected by Enterprise Grade Security</p>
            <p>© 2026 HCLTech • ModernSaaS v2.5</p>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)
    
    # RIGHT SIDE - Auth Card
    with col_right:
        # Tabs for Sign In / Create Account
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])

        with auth_tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="e.g. john.doe")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("<a href='#' style='color: #ef4444; font-size: 0.85rem; text-decoration: none;'>Forgot password?</a>", unsafe_allow_html=True)
                
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                
                if submit_login:
                    result = login_user(username, password)
                    if result["success"]:
                        st.session_state.logged_in = True
                        st.session_state.user = result["user"]
                        st.query_params["user"] = result["user"]["username"]
                        add_notification(f"Welcome back, {result['user']['full_name']}!", type="success")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")

        with auth_tab2:
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
                        st.error("❌ Email must be a valid @hcltech.ac.in address.")
                    else:
                        result = create_user(new_user, new_pass, full_name, email)
                        if result["success"]:
                            add_notification("Account created! Please log in.", type="success")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")

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

@st.dialog("🎫 Ticket Details")
def show_ticket_details(ticket):
    st.markdown(f"<h3 style='color:var(--text-primary);'>{ticket['ticket_id']}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:var(--text-secondary);'><b>Issue:</b> <span style='color:var(--text-main);'>{ticket['issue']}</span></p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 1px solid var(--border-color); margin: 15px 0;'>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    priority = ticket.get('priority', 'Medium')
    tag_color = "#ef4444" if priority == "High" else ("#f59e0b" if priority == "Medium" else "#3b82f6")
    
    with col_a:
        st.markdown(f"<p style='color:var(--text-primary);'><b>Priority:</b> <span style='color:{tag_color}; font-weight:bold;'>{priority}</span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-primary);'><b>Status:</b> {ticket['status']}</p>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<p style='color:var(--text-primary);'><b>Assigned To:</b> {ticket['assigned_to']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--text-primary);'><b>Created:</b> {ticket['created_at'][:10]}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border-top: 1px solid var(--border-color); margin: 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-primary); font-weight:bold;'>System Analysis:</p>", unsafe_allow_html=True)
    st.info(f"Ticket {ticket['ticket_id']} is currently being tracked. Initial triage categorizes this as a {priority} priority issue assigned to {ticket['assigned_to']}.")
    
    if st.button("Update Status", use_container_width=True):
        st.success("Triage updated (Simulation)")
    
    if st.button("Close Dialog", use_container_width=True):
        st.rerun()

# =========================================================
#                    MAIN APPLICATION
# =========================================================

# -------------------- HEADER --------------------
main_header_html = "<div class='main-header'><h1>🤖 HCLTech Enterprise Assistant</h1>" \
                   "<p>AI-Powered Support • Instant Issue Resolution • Smart Scheduling</p></div>"
st.markdown(main_header_html, unsafe_allow_html=True)


# -------------------- TABS --------------------
# Remove blue tab selection color
st.markdown("""
<style>
    [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--text-main) !important;
        border-bottom-color: transparent !important;
    }
    [data-baseweb="tab-list"] button[aria-selected="true"]:after {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📅 HR Meetings", "🎫 IT Tickets"])

# ==================== TAB 1: CHAT ASSISTANT ====================
with tab1:
    # Center the chat content
    st.markdown("""
    <style>
        .chat-wrapper {
            max-width: 900px;
            margin: 0 auto;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader(f"👋 Hi, {username_display}!")
    
    # -------- SESSION STATE --------
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        with st.spinner("🚀 Initializing secure enterprise environment..."):
            st.session_state.agent = get_agent()
    
    # -------- CHAT AREA (SCROLLABLE) --------
    # Dynamic height based on whether there are messages
    chat_height = 150 if not st.session_state.messages else 400
    chat_container = st.container(height=chat_height, border=False)
    
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 20px 40px; color: var(--text-secondary);">
                <h3 style="color: var(--text-primary);">How can I help you today?</h3>
                <p>I can help you schedule meetings, report IT issues, or answer company queries.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
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

        if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_actual_key_here":
            st.warning("⚠️ **AI Setup Required**")
            st.markdown(textwrap.dedent("""
                AI features like meeting scheduling and ticket resolution are currently disabled.
                
                1. Get your key at [Groq Console](https://console.groq.com/keys)
                2. Open `.env` in the root folder
                3. Replace the placeholder with your key:
                   `GROQ_API_KEY=gsk_...`
            """))
    
    # -------- INPUT FIELD (BELOW SCROLL) --------
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
        st.rerun()
    
    # Handle agent response separately (OUTSIDE chat container)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("⚡ Thinking..."):
            try:
                last_user_msg = st.session_state.messages[-1]["content"]
                result = st.session_state.agent.invoke(last_user_msg)
                response_text = result.get("output", "I apologize, but I couldn't process that request.")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # --- NEW: Trigger Browser Notification for Agent Update ---
                msg_preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                alert_type = "info"
                if "✅" in response_text or "confirmed" in response_text.lower() or "scheduled" in response_text.lower():
                    alert_type = "success"
                elif "⚠️" in response_text or "error" in response_text.lower() or "failed" in response_text.lower():
                    alert_type = "warning"
                
                add_notification(f"AI Update: {msg_preview}", type=alert_type)
                
                st.rerun()
            except Exception as e:
                error_msg = f"I encountered an error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.rerun()

# ==================== TAB 2: HR MEETINGS ====================
with tab2:
    meetings_data = get_all_meetings()
    
    if meetings_data:
        col_header, col_export = st.columns([3, 1])
        with col_header:
            st.subheader("📅 Meeting Scheduler Dashboard")
        with col_export:
            st.download_button(
                label="📥 Download JSON",
                data=pd.DataFrame(meetings_data).to_json(orient="records", indent=4),
                file_name="meetings_export.json",
                mime="application/json",
                use_container_width=True,
                key="tab_export_meetings"
            )
        for meeting in meetings_data[::-1]:
            # Create a card container
            with st.container():
                status_class = "tag-green" if meeting['status'] == "Scheduled" else "tag-blue"
                meeting_html = f"<div class='card priority-low' style='margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;'>" \
                               f"<div style='display:flex; justify-content:space-between; align-items:start;'><div>" \
                               f"<h4 style='color:var(--text-primary); margin-bottom:0;'>{meeting['department']} Department</h4>" \
                               f"<p style='color:var(--text-secondary); margin-top:5px;'>{meeting['reason']}</p>" \
                               f"<span class='tag tag-blue'>{meeting['meeting_id']}</span> " \
                               f"<span class='tag {status_class}'>{meeting['status']}</span></div>" \
                               f"<div style='text-align:right; font-size:0.85rem; color:var(--text-secondary);'>" \
                               f"<p style='margin:0;'>{meeting['created_at'][:10]}</p>" \
                               f"<p style='margin:0;'>{meeting['created_at'][11:16]}</p></div></div></div>"
                st.markdown(meeting_html, unsafe_allow_html=True)
                
                # Use st.columns to put the user info and button in the same row
                card_footer = st.container()
                with card_footer:
                    # CSS-like styling for the bottom part of the card
                    st.markdown("<div style='background:var(--bg-card); padding: 0px 24px 20px 24px; border: 1px solid var(--border-color); border-top: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;'>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-top: 10px;'><div style='width:24px; height:24px; background:var(--bubble-user); border-radius:50%; display:flex; align-items:center; justify-content:center; color:var(--bubble-user-text); font-size:12px; font-weight:bold;'>{meeting['user_name'][0]}</div><span style='font-size:0.9rem; color:var(--text-primary);'>{meeting['user_name']}</span></div>", unsafe_allow_html=True)
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
                label="📥 Download JSON",
                data=pd.DataFrame(tickets_data).to_json(orient="records", indent=4),
                file_name="tickets_export.json",
                mime="application/json",
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
                priority = ticket.get('priority', 'Medium')
                priority_class = f"priority-{priority.lower()}"
                tag_class = "tag-red" if priority == "High" else ("tag-orange" if priority == "Medium" else "tag-blue")
                
                ticket_html = f"<div class='card {priority_class}' style='margin-bottom:0px; border-bottom-left-radius:0px; border-bottom-right-radius:0px;'><div style='display:flex; justify-content:space-between; align-items:start;'>" \
                              f"<h4 style='color:var(--text-primary); margin-bottom:0;'>{ticket['ticket_id']}</h4>" \
                              f"<span class='tag {tag_class}'>{priority} Priority</span></div>" \
                              f"<p style='margin-top:15px; font-weight:600; color:var(--text-primary); font-size:1.1rem;'>{ticket['issue']}</p>" \
                              f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:15px;'>" \
                              f"<span style='font-size:0.85rem; padding:4px 8px; background:rgba(255,255,255,0.05); border-radius:4px;'>👤 {ticket['assigned_to']}</span></div></div>"
                st.markdown(ticket_html, unsafe_allow_html=True)
                
                # Ticket Footer with Functional Button
                ticket_footer = st.container()
                with ticket_footer:
                    st.markdown("<div style='background:var(--bg-card); padding: 0px 24px 20px 24px; border: 1px solid var(--border-color); border-top: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;'>", unsafe_allow_html=True)
                    f_col1, f_col2 = st.columns([1.5, 1])
                    with f_col1:
                        st.markdown(f"<span style='font-size:0.8rem; color:var(--text-secondary); opacity:0.8; display:block; margin-top:12px;'>Created: {ticket['created_at'][:10]}</span>", unsafe_allow_html=True)
                    with f_col2:
                        if st.button("View Details →", key=f"tkt_{ticket['ticket_id']}", use_container_width=True):
                            show_ticket_details(ticket)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:50px;">
            <h3>All systems operational</h3>
            <p style="color:var(--text-secondary);">No open support tickets found.</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------- GLOBAL BROWSER ALERTS RENDERER --------------------
# This block processes the pending_alerts queue and triggers native notifications
if st.session_state.get('pending_alerts'):
    for alert in st.session_state.pending_alerts:
        msg = alert["message"]
        alert_type = alert.get("type", "info")
        
        # Select premium icon based on type
        icon_url = "https://cdn-icons-png.flaticon.com/512/2593/2593635.png" # Default Robot
        if alert_type == "success":
            icon_url = "https://cdn-icons-png.flaticon.com/512/11433/11433361.png" # Success Check
        elif alert_type == "warning":
            icon_url = "https://cdn-icons-png.flaticon.com/512/564/564619.png" # Warning
        elif alert_type == "error":
            icon_url = "https://cdn-icons-png.flaticon.com/512/564/564619.png" # Error
            
        st.markdown(f"""
        <script>
            if (window.Notification && Notification.permission === "granted") {{
                new Notification("HCLTech Enterprise Assistant", {{
                    body: "{msg}",
                    icon: "{icon_url}",
                    tag: "hcltech-alert",
                    badge: "https://cdn-icons-png.flaticon.com/512/2593/2593635.png"
                }});
            }} else if (window.Notification && Notification.permission !== "denied") {{
                Notification.requestPermission();
            }}
        </script>
        """, unsafe_allow_html=True)
    # Clear the queue after rendering
    st.session_state.pending_alerts = []